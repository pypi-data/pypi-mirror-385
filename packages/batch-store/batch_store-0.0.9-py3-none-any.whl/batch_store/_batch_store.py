import asyncio
import json
import math
import random
import re
import time
import traceback
from pathlib import Path

import pandas as pd
from pydantic import BaseModel
from util_common.decorator import deprecated
from util_common.io_util import json2bytes
from util_common.list_util import in_batches
from util_common.path import EXCEL_EXTS, duplicate, ensure_folder, sort_paths, split_basename

from batch_store._log import logger
from batch_store.preprocessors import (
    close_all_clients,
    decompress_sample_and_save,
    request_unify_pages,
    save_unified_file,
    unify_pages_and_save,
)
from batch_store.settings import batch_store_settings


class TagRecord(BaseModel):
    batch_name: str
    sample_name: str
    page_name: str
    tag: str


class Page(BaseModel):
    name: str
    page_dir: Path


class Sample(BaseModel):
    name: str
    sample_dir: Path
    pages: list[Page]


class SplitCount(BaseModel):
    train: int = 0
    eval: int = 0
    test: int = 0


class SplitCounts(BaseModel):
    sample_level: SplitCount = SplitCount()
    page_level: SplitCount = SplitCount()


class SplitedSampleNames(BaseModel):
    train: list[str] = []
    eval: list[str] = []
    test: list[str] = []


class SplitDict(BaseModel):
    counts: SplitCounts = SplitCounts()
    samples: SplitedSampleNames = SplitedSampleNames()


class BatchStore:
    """
    功能:
    对一个批次内的样本进行统一的数据预处理, 以及存储操作, 并提供一些辅助功能

    目录结构:
    不指定 batch_dir 时, 数据根目录结构:
    |-batch_store_settings.data_root
    |   |-batches
    |   |   |-batch-1
    |   |   |   |-raw:
    |   |   |   |   |-sample_1.zip
    |   |   |   |   |-sample_2
    |   |   |   |   |-sample_3.pdf
    |   |   |   |   |-sample_4.xls
    |   |   |   |   |-...

    指定 batch_dir 时, 数据根目录结构:
    |-batch_dir
    |   |-raw:
    |   |   |-sample_1.zip
    |   |   |-sample_2
    |   |   |-sample_3.pdf
    |   |   |-sample_4.xls
    |   |   |-...

    依赖:
    解压缩服务
    文件归一化服务

    使用方法:
    配置环境变量 DATA_ROOT 为数据根目录
    配置环境变量 DECOMPRESS_BASE_URL 为解压缩服务地址
    配置环境变量 UNIFY_BASE_URL 为文件归一化服务地址

    使用示例:
    batch_store = BatchStore('batch-1')
    asyncio.run(batch_store.preprocess_batch())
    """

    def __init__(self, batch_name: str | None = None, batch_dir: Path | None = None) -> None:
        if batch_name is None and batch_dir is None:
            raise ValueError('batch_name or batch_dir must be provided')
        if batch_name is not None and batch_dir is not None:
            if batch_dir.name != batch_name:
                raise ValueError('batch_name and batch_dir must have the same name')
        self.batch_name = batch_name or batch_dir.name  # type: ignore
        self.batch_dir = batch_dir or batch_store_settings.data_root / 'batches' / self.batch_name
        self.raw_dir = self.batch_dir / 'raw'
        self.decompressed_dir = self.batch_dir / 'decompressed'
        self.unified_dir = self.batch_dir / 'unified'
        self.failed_dir = self.batch_dir / 'failed'
        self.results_dir = self.batch_dir / 'result'  # 端到端结果存放
        self.tag_dir = self.batch_dir / 'tag'  # 端到端标签存放
        self.compare_dir = self.batch_dir / 'compare'  # 端到端结果对比
        self.task_results_dir = self.batch_dir / 'task_results'  # 单任务结果存放
        self.task_tag_dir = self.batch_dir / 'task_tags'  # 单任务标签存放
        self.task_compare_dir = self.batch_dir / 'task_compares'  # 单任务结果对比
        self.classified_dir = (
            self.batch_dir / 'classified'
        )  # 按照分类标签分拣到对应文件夹下用来查看
        self.sessions_dir = (
            self.batch_dir / 'sessions'
        )  # 保存一次运行会话的上下文信息, 应当包含方法/任务ID, 会话ID, 测试ID, 运行时间, 运行参数, 结果路径等
        self.split_dict_path = self.batch_dir / 'split_dict.json'
        self.tagging_status_path = self.batch_dir / 'tagging_status.json'

    async def _preprocess_sample(
        self,
        sample_path: Path,
        target_results: list[str] = [],
        fix_broken: bool = False,
        check_empty: bool = False,
    ) -> None:
        save_dir = self.unified_dir / sample_path.name
        if fix_broken and save_dir.is_dir():
            return
        try:
            if check_empty is True:
                for page_dir in sort_paths(save_dir.iterdir()):
                    if page_dir.joinpath('pure.txt').read_text().strip():
                        continue
                    if not page_dir.joinpath('raw.pdf').exists():
                        continue
                    logger.info(f'Checking empty page: {page_dir.name} ...')
                    success_pages, failed_files = await request_unify_pages(
                        page_dir.joinpath('raw.pdf').name,
                        page_dir.joinpath('raw.pdf').read_bytes(),
                        target_results,
                    )
                    if len(success_pages) == 1:
                        await save_unified_file(page_dir, success_pages[0])
                        if page_dir.joinpath('pure.txt').read_text().strip():
                            logger.info(f'Extract page success: {page_dir.name}')
                        else:
                            logger.info(f'Empty page checked! {page_dir.name}')
                    else:
                        logger.error(f'Check empty page failed! {page_dir.name}')
            else:
                file_paths = await decompress_sample_and_save(
                    sample_path, self.decompressed_dir, self.failed_dir
                )
                await asyncio.gather(
                    *[
                        unify_pages_and_save(
                            file_path,
                            save_dir,
                            self.failed_dir,
                            target_results,
                        )
                        for file_path in file_paths
                    ]
                )
        except Exception:
            logger.error(f"Error processing sample {sample_path}: {traceback.format_exc()}")
            duplicate(sample_path, self.failed_dir / sample_path.name)

    async def preprocess_batch(
        self,
        target_results: list[str] = [],
        concurrency: int = 1,
        failed_only: bool = False,  # 只需要运行 failed 下的样本
        fix_broken: bool = False,  # 跳过已经处理过的样本
        check_empty: bool = False,  # 检查样本 pure.txt 是否为空, 如果为空再试一次
    ) -> None:
        """Process all samples in the batch with proper error handling."""
        # Ensure all required directories exist
        for dir_path in [
            self.raw_dir,
            self.decompressed_dir,
            self.unified_dir,
            self.failed_dir,
        ]:
            ensure_folder(dir_path)

        try:
            if failed_only:
                sample_paths = sort_paths(self.failed_dir.iterdir())
            else:
                sample_paths = sort_paths(self.raw_dir.iterdir())

            for i, batch in enumerate(in_batches(sample_paths, concurrency)):
                start_time = time.time()
                await asyncio.gather(
                    *[
                        self._preprocess_sample(
                            sample_path, target_results, fix_broken, check_empty
                        )
                        for sample_path in batch
                    ]
                )
                end_time = time.time()
                logger.info(
                    f'### Preprocess batch {i + 1} finished in {end_time - start_time:.2f} seconds'
                )
        except Exception as e:
            logger.error(f"Error in preprocess_batch: {traceback.format_exc()}")
            raise e
        finally:
            await close_all_clients()

    def load_unified_samples(self) -> list[Sample]:
        samples = []
        for sample_dir in sort_paths(self.unified_dir.iterdir()):
            pages = []
            for page_dir in sort_paths(sample_dir.iterdir()):
                pages.append(Page(name=page_dir.name, page_dir=page_dir))
            samples.append(Sample(name=sample_dir.name, sample_dir=sample_dir, pages=pages))
        return samples

    def save_sample(self, content: bytes, file_name: str):
        save_path = self.raw_dir / file_name
        ensure_folder(save_path.parent)
        save_path.write_bytes(content)

    def split_dataset(
        self,
        train_proportion: float = 0.8,
        eval_proportion: float = 0.1,
        test_proportion: float = 0.1,
        seed: int = 42,
        update_proportion: bool = False,
    ) -> SplitDict:
        """
        Split the dataset into train, eval and test sets.
        自动删除实际不存在的样本, 更新新加入的样本。
        如果 update_proportion 为 False, 不会更新旧样本的数据的 split_type, 只会给新加入的数据按比例分配。
        """
        total_proportion = train_proportion + eval_proportion + test_proportion
        if not math.isclose(total_proportion, 1.0, rel_tol=1e-9, abs_tol=1e-9):
            message = (
                'train_proportion + eval_proportion + test_proportion must be 1 '
                f'(got {total_proportion:.12f})'
            )
            raise ValueError(message)

        random.seed(seed)
        samples = self.load_unified_samples()
        if self.split_dict_path.exists():
            split_dict = SplitDict.model_validate_json(self.split_dict_path.read_text())
        else:
            split_dict = SplitDict()

        actual_train_samples: list[str] = []
        actual_eval_samples: list[str] = []
        actual_test_samples: list[str] = []

        train_page_counts = 0
        eval_page_counts = 0
        test_page_counts = 0
        for sample in samples:
            if sample.name in split_dict.samples.train:
                actual_train_samples.append(sample.name)
                train_page_counts += len(sample.pages)
            elif sample.name in split_dict.samples.eval:
                actual_eval_samples.append(sample.name)
                eval_page_counts += len(sample.pages)
            elif sample.name in split_dict.samples.test:
                actual_test_samples.append(sample.name)
                test_page_counts += len(sample.pages)
            else:
                _random = random.random()
                if _random <= train_proportion:
                    actual_train_samples.append(sample.name)
                    train_page_counts += len(sample.pages)
                elif _random <= train_proportion + eval_proportion:
                    actual_eval_samples.append(sample.name)
                    eval_page_counts += len(sample.pages)
                else:
                    actual_test_samples.append(sample.name)
                    test_page_counts += len(sample.pages)
        if update_proportion:
            raise NotImplementedError('update_proportion is not implemented')
        split_dict = SplitDict(
            counts=SplitCounts(
                sample_level=SplitCount(
                    train=len(actual_train_samples),
                    eval=len(actual_eval_samples),
                    test=len(actual_test_samples),
                ),
                page_level=SplitCount(
                    train=train_page_counts,
                    eval=eval_page_counts,
                    test=test_page_counts,
                ),
            ),
            samples=SplitedSampleNames(
                train=actual_train_samples,
                eval=actual_eval_samples,
                test=actual_test_samples,
            ),
        )
        self.split_dict_path.write_text(split_dict.model_dump_json(indent=4))
        return split_dict

    def get_split_dict(
        self,
        check_updated: bool = False,
        train_proportion: float | None = None,
        eval_proportion: float | None = None,
        test_proportion: float | None = None,
    ) -> SplitDict:
        if check_updated is False and self.split_dict_path.exists():
            return SplitDict.model_validate_json(self.split_dict_path.read_text())
        # If any proportion is provided, require all three and pass through; else, use defaults
        provided_any = (
            train_proportion is not None
            or eval_proportion is not None
            or test_proportion is not None
        )
        if provided_any:
            if train_proportion is None or eval_proportion is None or test_proportion is None:
                raise ValueError(
                    '请同时提供训练/验证/测试比例: '
                    'train_proportion, eval_proportion, test_proportion'
                )
            self.split_dataset(
                train_proportion=train_proportion,
                eval_proportion=eval_proportion,
                test_proportion=test_proportion,
            )
        else:
            logger.warning('没有提供训练/验证/测试比例, 使用默认比例: 0.8, 0.1, 0.1')
            self.split_dataset()
        return self.get_split_dict(check_updated=False)

    def get_result_dir(
        self,
        method_id: str | None = None,
        session_id: int | None = None,
        test_id: str | None = None,
    ) -> Path | None:
        if method_id is None or session_id is None:
            return None
        result_dir = self.results_dir / f'{method_id}-{session_id}'
        if test_id:
            result_dir = result_dir / test_id
        return result_dir

    def save_sample_result(
        self,
        sample_name: str,
        result: list[dict] | dict,
        save_dir: Path | None = None,
        method_id: str | None = None,
        session_id: int | None = None,
        test_id: str | None = None,
    ):
        """
        method_id: 方法ID, 运行主要方法
        session_id: 会话ID, 该方法固定参数下运行的一次会话
        test_id: 测试ID, 同一会话重复运行多次的试验
        """
        if save_dir is None:
            save_dir = self.get_result_dir(method_id, session_id, test_id)
        if save_dir is None:
            raise ValueError(
                f"Result save directory not found: \n\n"
                f"save_dir - {save_dir}, \n\n"
                f"method_id - {method_id}, \n\n"
                f"session_id - {session_id}, \n\n"
                f"test_id - {test_id}"
            )
        save_dir.mkdir(parents=True, exist_ok=True)
        save_path = save_dir / f'{sample_name}.json'
        save_path.write_bytes(json2bytes(result))

    def get_sample_result(
        self,
        sample_name,
        result_dir: Path | None = None,
        method_id: str | None = None,
        session_id: int | None = None,
        test_id: str | None = None,
    ):
        if result_dir is None:
            result_dir = self.get_result_dir(method_id, session_id, test_id)
        if result_dir is None:
            raise ValueError(
                f"Result directory not found: \n\n"
                f"result_dir - {result_dir}, \n\n"
                f"method_id - {method_id}, \n\n"
                f"session_id - {session_id}, \n\n"
                f"test_id - {test_id}"
            )
        result_path = result_dir / f'{sample_name}.json'
        if not result_path.exists():
            raise ValueError(f"Result file {result_path} not found")
        return json.loads(result_path.read_text())

    def get_task_result_dir(
        self,
        task_id: str | None = None,
        session_id: int | None = None,
        test_id: str | None = None,
    ) -> Path | None:
        if task_id is None or session_id is None:
            return None
        result_dir = self.task_results_dir / task_id / f'{task_id}-{session_id}'
        if test_id:
            result_dir = result_dir / test_id
        return result_dir

    @deprecated(replacement='get_task_result_dir')
    def get_sample_task_result_dir(
        self,
        task_id: str | None = None,
        session_id: int | None = None,
        test_id: str | None = None,
    ) -> Path | None:
        return self.get_task_result_dir(task_id, session_id, test_id)

    def save_sample_task_result(
        self,
        sample_name: str,
        result: list[dict] | dict | bytes,
        save_dir: Path | None = None,
        task_id: str | None = None,
        session_id: int | None = None,
        test_id: str | None = None,
        suffix: str = 'json',
    ):
        """
        task_id: 任务ID
        session_id: 会话ID, 该任务固定参数下运行的一次会话
        test_id: 测试ID, 同一会话重复运行多次的试验
        suffix: 结果文件后缀
        """
        if save_dir is None:
            save_dir = self.get_sample_task_result_dir(task_id, session_id, test_id)
        if save_dir is None:
            raise ValueError(
                f"Result save directory not found: \n\n"
                f"save_dir - {save_dir}, \n\n"
                f"task_id - {task_id}, \n\n"
                f"session_id - {session_id}, \n\n"
                f"test_id - {test_id}"
            )
        save_dir.mkdir(parents=True, exist_ok=True)
        save_path = save_dir / f'{sample_name}.{suffix}'
        try:
            if suffix == 'json':
                save_path.write_bytes(json2bytes(result))  # type: ignore
            else:
                save_path.write_bytes(result)  # type: ignore
        except Exception:
            raise ValueError(f"Invalid result: {str(result)[:100]}")

    def get_sample_task_result(
        self,
        sample_name,
        result_dir: Path | None = None,
        task_id: str | None = None,
        session_id: int | None = None,
        test_id: str | None = None,
        suffix: str = 'json',
    ):
        if result_dir is None:
            result_dir = self.get_sample_task_result_dir(task_id, session_id, test_id)
        if result_dir is None:
            raise ValueError(
                f"Task result directory not found: \n\n"
                f"result_dir - {result_dir}, \n\n"
                f"task_id - {task_id}, \n\n"
                f"session_id - {session_id}, \n\n"
                f"test_id - {test_id}"
            )
        result_path = result_dir / f'{sample_name}.{suffix}'
        if not result_path.exists():
            raise ValueError(f"Result file {result_path} not found")
        if suffix == 'json':
            return json.loads(result_path.read_text())
        else:
            return result_path.read_bytes()

    def save_session_info(
        self,
        session_info: dict,
        method_or_task_id: str,
        session_id: int,
    ) -> None:
        session_info_path = (
            self.sessions_dir / method_or_task_id / f'{method_or_task_id}-{session_id}.json'
        )
        ensure_folder(session_info_path.parent)
        session_info_path.write_bytes(json2bytes(session_info))

    def get_task_compare_dir(self, task_id: str, session_id: int, test_id: str | None = None):
        compare_dir = self.task_compare_dir / task_id / f'{task_id}-{session_id}'
        if test_id:
            compare_dir = compare_dir / test_id
        compare_dir.mkdir(parents=True, exist_ok=True)
        return compare_dir

    def backup_tag(self, tag_name: str):
        records = []
        for sample_dir in sort_paths(self.unified_dir.iterdir()):
            for page_dir in sort_paths(sample_dir.iterdir()):
                tag_path = page_dir / f"tag-{tag_name}.json"
                if tag_path.exists():
                    record = TagRecord(
                        batch_name=self.batch_name,
                        sample_name=sample_dir.name,
                        page_name=page_dir.name,
                        tag=tag_path.read_text(),
                    )
                    records.append(record.model_dump())

        df = pd.DataFrame.from_records(records)
        logger.info(f'Saving {tag_name}.csv...')
        logger.info(f'total {df.shape[0]} records')
        logger.info(f'first 5 records: {df.head()}')
        logger.info(f'last 5 records: {df.tail()}')
        ensure_folder(self.task_tag_dir)
        df.to_csv(f'{self.task_tag_dir}/{tag_name}.csv', index=False)

    def restore_tag(self, tag_name: str):
        df = pd.read_csv(f'{self.task_tag_dir}/{tag_name}.csv')
        for _, row in df.iterrows():
            sample_name = row['sample_name']
            page_name = row['page_name']
            tag = row['tag']
            save_path = self.unified_dir / sample_name / page_name / f'tag-{tag_name}.json'
            try:
                save_path.write_text(tag)  # type: ignore
            except Exception:
                logger.error(f'{sample_name} {page_name} {tag_name} restore failed, skip')

    @staticmethod
    def get_unified_page_dir(batch_root: Path, batch_name: str, sample_name: str, page_name: str):
        return batch_root / batch_name / 'unified' / sample_name / page_name

    @staticmethod
    def split_page_name(page_name: str) -> tuple[str | None, int, str | None]:
        def get_filename(stem: str, span: tuple[int, int]) -> str:
            filename = stem[: span[0]]
            if len(filename.split('-')) > 1:
                filename = '-'.join(filename.split('-')[1:])
            return filename

        def get_page_id_and_sheetname(stem: str, span: tuple[int, int]) -> tuple[int, str]:
            src_segment = stem[span[0] :]
            match = re.match(r'-p\d+_', src_segment)
            sheetname = ''
            page_id = 0
            if match:
                span = match.span()
                sheetname = src_segment[span[1] :]
                page_id = int(src_segment[2 : span[1] - 1])
            return page_id, sheetname

        def get_page_id(stem: str, span: tuple[int, int]) -> int:
            src_segment = stem[span[0] :]
            match = re.match(r'-p\d+$', src_segment)
            page_id = 0
            if match:
                span = match.span()
                page_id = int(src_segment[2 : span[1]])
            return page_id

        stem, suffix = split_basename(page_name)
        filename = None
        sheetname = None
        page_id = 0
        if suffix in EXCEL_EXTS:
            match = re.search(fr'-p\d+_.+\.{suffix}$', page_name)
            if match:
                span = match.span()
                filename = get_filename(stem, span)
                page_id, sheetname = get_page_id_and_sheetname(stem, span)
        else:
            match = re.search(fr'-p\d+\.{suffix}$', page_name)
            if match:
                span = match.span()
                filename = get_filename(stem, span)
                page_id = get_page_id(stem, span)
        return filename, page_id, sheetname


if __name__ == '__main__':
    filename, page_id, sheetname = BatchStore.split_page_name('test-p1.pdf')
    print(filename, page_id, sheetname)
