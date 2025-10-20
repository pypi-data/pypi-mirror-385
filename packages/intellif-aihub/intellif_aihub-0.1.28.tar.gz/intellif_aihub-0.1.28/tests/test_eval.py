# !/usr/bin/env python
# -*-coding:utf-8 -*-
import json
import os
import unittest
from unittest.mock import Mock, patch

import httpx

from aihub.models.artifact import ArtifactType
from aihub.models.eval import ListEvalResp, MetricsArtifact
from aihub.services.eval import EvalService
from src.aihub.client import Client

BASE_URL = "http://192.168.13.160:30021"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NjEyMTA2MDIsImlhdCI6MTc2MDYwNTgwMiwidWlkIjoyfQ.BbT_PsExPIHRiWVUwqDapxgeCc4W3dVXI2z-jrxZGnc"


class TestEvalService(unittest.TestCase):

    def setUp(self):
        self.http_client = Mock(spec=httpx.Client)
        self.eval_service = EvalService(self.http_client)

    def test_list_eval_runs_default(self):
        mock_eval_run = {
            "id": 1,
            "name": "test_eval",
            "description": "Test evaluation",
            "user_id": 1,
            "model_id": 1,
            "model_name": "test_model",
            "dataset_id": 1,
            "dataset_version_id": 1,
            "dataset_name": "test_dataset",
            "status": "completed",
            "prediction_artifact_path": "/path/to/prediction",
            "evaled_artifact_path": "/path/to/eval",
            "run_id": "test_run_123",
            "dataset_summary": {},
            "metrics_summary": {"accuracy": 0.95},
            "viz_summary": {},
            "eval_config": {"metric": "accuracy"},
            "created_at": 1640995200,
            "updated_at": 1640995200,
        }

        mock_response = {
            "code": 0,
            "msg": None,
            "data": {"total": 1, "page_size": 20, "page_num": 1, "data": [mock_eval_run]},
        }

        mock_resp = Mock()
        mock_resp.json.return_value = mock_response
        self.http_client.get.return_value = mock_resp

        result = self.eval_service.list()

        self.assertIsInstance(result, ListEvalResp)
        self.assertEqual(result.total, 1)
        self.assertEqual(result.page_size, 20)
        self.assertEqual(result.page_num, 1)
        self.assertEqual(len(result.data), 1)
        self.assertEqual(result.data[0].id, 1)
        self.assertEqual(result.data[0].name, "test_eval")

        self.http_client.get.assert_called_once_with(
            "/eval-platform/api/v1/run/", params={"page_size": 20, "page_num": 1}
        )

    def test_list_eval_runs_with_filters(self):
        mock_response = {"code": 0, "msg": None, "data": {"total": 0, "page_size": 10, "page_num": 1, "data": []}}

        mock_resp = Mock()
        mock_resp.json.return_value = mock_response
        self.http_client.get.return_value = mock_resp

        # 带过滤参数
        result = self.eval_service.list(
            page_size=10,
            page_num=1,
            status="completed",
            name="test",
            model_id=1,
            dataset_id=2,
            dataset_version_id=3,
            run_id="test_run",
            user_id=1,
            model_ids="1,2,3",
            dataset_ids="2,3,4",
            dataset_version_ids="3,4,5",
        )

        self.assertIsInstance(result, ListEvalResp)
        self.assertEqual(result.total, 0)
        self.assertEqual(len(result.data), 0)

        expected_params = {
            "page_size": 10,
            "page_num": 1,
            "status": "completed",
            "name": "test",
            "model_id": 1,
            "dataset_id": 2,
            "dataset_version_id": 3,
            "run_id": "test_run",
            "user_id": 1,
            "model_ids": "1,2,3",
            "dataset_ids": "2,3,4",
            "dataset_version_ids": "3,4,5",
        }
        self.http_client.get.assert_called_once_with("/eval-platform/api/v1/run/", params=expected_params)

    def test_list_eval_runs_api_error(self):
        """测试列出评测运行 - API错误"""
        # 模拟 API 错误
        mock_response = {"code": 1001, "msg": "Database connection failed", "data": None}

        mock_resp = Mock()
        mock_resp.json.return_value = mock_response
        self.http_client.get.return_value = mock_resp

        with self.assertRaises(Exception) as context:
            self.eval_service.list()

        self.assertIn("backend code 1001", str(context.exception))
        self.assertIn("Database connection failed", str(context.exception))

    def test_list_eval_runs_only_specified_filters(self):
        mock_response = {"code": 0, "msg": None, "data": {"total": 0, "page_size": 20, "page_num": 1, "data": []}}

        mock_resp = Mock()
        mock_resp.json.return_value = mock_response
        self.http_client.get.return_value = mock_resp

        result = self.eval_service.list(status="completed", model_id=1)

        expected_params = {"page_size": 20, "page_num": 1, "status": "completed", "model_id": 1}
        self.http_client.get.assert_called_once_with("/eval-platform/api/v1/run/", params=expected_params)

    @patch("aihub.services.dataset_management.DatasetManagementService")
    def test_create_eval_llm_default_user_id(self, mock_dataset_service_class):
        """测试创建 LLM 类型评测 - 使用默认 user_id"""
        # 模拟数据集版本
        mock_dataset_version = Mock()
        mock_dataset_version.dataset_id = 1
        mock_dataset_version.id = 1

        mock_dataset_service = Mock()
        mock_dataset_service.get_dataset_version_by_name.return_value = mock_dataset_version
        mock_dataset_service_class.return_value = mock_dataset_service

        # 模拟成功的创建响应
        mock_eval_run = {
            "id": 123,
            "name": "test_eval",
            "description": "Test evaluation",
            "user_id": 0,
            "model_id": 1,
            "model_name": "test_model",
            "dataset_id": 1,
            "dataset_version_id": 1,
            "dataset_name": "test_dataset",
            "status": "created",
            "prediction_artifact_path": "/path/to/prediction.json",
            "evaled_artifact_path": "/path/to/evaled.json",
            "run_id": "test_run_123",
            "dataset_summary": {},
            "metrics_summary": {},
            "viz_summary": {},
            "eval_config": None,
            "created_at": 1640995200,
            "updated_at": 1640995200,
        }

        mock_response = {"code": 0, "msg": None, "data": {"eval_run": mock_eval_run}}

        mock_resp = Mock()
        mock_resp.json.return_value = mock_response
        self.http_client.post.return_value = mock_resp

        # 调用方法（不提供 user_id，使用默认值）
        result = self.eval_service.create(
            dataset_version_name="test_dataset_v1",
            prediction_artifact_path="/path/to/prediction.json",
            evaled_artifact_path="/path/to/evaled.json",
            report_json={"accuracy": 0.95},
            run_id="test_run_123",
        )

        # 验证结果
        self.assertEqual(result, 123)

        # 验证 HTTP 调用
        self.http_client.post.assert_called_once()
        call_args = self.http_client.post.call_args

        # 验证端点
        self.assertEqual(call_args[0][0], "/eval-platform/api/v1/run/")

        # 验证 payload 内容
        actual_payload = call_args[1]["json"]

        # 验证 LLM 类型必需字段
        self.assertEqual(actual_payload["run_id"], "test_run_123")
        self.assertEqual(actual_payload["type"], "llm")
        self.assertEqual(actual_payload["prediction_artifact_path"], "/path/to/prediction.json")
        self.assertEqual(actual_payload["user_id"], 0)
        self.assertEqual(actual_payload["dataset_id"], 1)
        self.assertEqual(actual_payload["dataset_version_id"], 1)
        self.assertEqual(actual_payload["evaled_artifact_path"], "/path/to/evaled.json")
        self.assertEqual(actual_payload["report"], {"accuracy": 0.95})

        # CV 类型字段不会出现在 LLM 类型评测的 payload 中
        self.assertNotIn("metrics_artifact_path", actual_payload)
        self.assertNotIn("ground_truth_artifact_path", actual_payload)

    @patch("aihub.services.dataset_management.DatasetManagementService")
    def test_create_eval_llm_custom_user_id(self, mock_dataset_service_class):
        """测试创建 LLM 类型评测 - 自定义 user_id"""
        # 模拟数据集版本
        mock_dataset_version = Mock()
        mock_dataset_version.dataset_id = 2
        mock_dataset_version.id = 3

        mock_dataset_service = Mock()
        mock_dataset_service.get_dataset_version_by_name.return_value = mock_dataset_version
        mock_dataset_service_class.return_value = mock_dataset_service

        # 模拟成功的创建响应
        mock_eval_run = {
            "id": 456,
            "name": "test_eval",
            "description": "Test evaluation",
            "user_id": 3750,
            "model_id": 1,
            "model_name": "test_model",
            "dataset_id": 2,
            "dataset_version_id": 3,
            "dataset_name": "test_dataset",
            "status": "created",
            "prediction_artifact_path": "/path/to/prediction.json",
            "evaled_artifact_path": "/path/to/evaled.json",
            "run_id": "test_run_456",
            "dataset_summary": {},
            "metrics_summary": {},
            "viz_summary": {},
            "eval_config": None,
            "created_at": 1640995200,
            "updated_at": 1640995200,
        }

        mock_response = {"code": 0, "msg": None, "data": {"eval_run": mock_eval_run}}

        mock_resp = Mock()
        mock_resp.json.return_value = mock_response
        self.http_client.post.return_value = mock_resp

        # 调用方法（提供自定义 user_id）
        result = self.eval_service.create(
            dataset_version_name="test_dataset_v2",
            prediction_artifact_path="/path/to/prediction.json",
            evaled_artifact_path="/path/to/evaled.json",
            report_json={"f1_score": 0.88},
            run_id="test_run_456",
            user_id=3750,
        )

        # 验证结果
        self.assertEqual(result, 456)

        # 验证 HTTP 调用
        self.http_client.post.assert_called_once()
        call_args = self.http_client.post.call_args
        actual_payload = call_args[1]["json"]

        # 验证关键字段
        self.assertEqual(actual_payload["type"], "llm")
        self.assertEqual(actual_payload["user_id"], 3750)
        self.assertEqual(actual_payload["dataset_id"], 2)
        self.assertEqual(actual_payload["dataset_version_id"], 3)

    def test_create_cv_run_default_user_id(self):
        """测试创建 CV 类型评测运行 - 使用默认 user_id"""
        # 模拟成功的创建响应
        mock_eval_run = {
            "id": 789,
            "name": "cv_eval",
            "description": "CV evaluation",
            "user_id": 0,
            "model_id": 2,
            "model_name": "cv_model",
            "dataset_id": 0,  # 使用默认值而不是 None
            "dataset_version_id": 0,  # 使用默认值而不是 None
            "dataset_name": "",  # 使用空字符串而不是 None
            "status": "created",
            "prediction_artifact_path": "coco_dt.json",
            "evaled_artifact_path": "",  # 使用空字符串而不是 None
            "run_id": "cv_run_789",
            "dataset_summary": {},
            "metrics_summary": {},
            "viz_summary": {},
            "eval_config": None,
            "created_at": 1640995200,
            "updated_at": 1640995200,
        }

        mock_response = {"code": 0, "msg": None, "data": {"eval_run": mock_eval_run}}

        mock_resp = Mock()
        mock_resp.json.return_value = mock_response
        self.http_client.post.return_value = mock_resp

        # 调用方法（不提供 user_id，使用默认值）
        result = self.eval_service.create_cv_run(
            run_id="cv_run_789",
            prediction_artifact_path="coco_dt.json",
            metrics_artifact_path="metrics.json",
            ground_truth_artifact_path="coco_gt.json",
        )

        # 验证结果
        self.assertEqual(result, 789)

        # 验证 HTTP 调用
        self.http_client.post.assert_called_once()
        call_args = self.http_client.post.call_args
        actual_payload = call_args[1]["json"]

        # 验证 CV 类型必需字段
        self.assertEqual(actual_payload["type"], "cv")
        self.assertEqual(actual_payload["user_id"], 0)
        self.assertEqual(actual_payload["run_id"], "cv_run_789")
        self.assertEqual(actual_payload["prediction_artifact_path"], "coco_dt.json")
        self.assertEqual(actual_payload["metrics_artifact_path"], "metrics.json")
        self.assertEqual(actual_payload["ground_truth_artifact_path"], "coco_gt.json")

        # LLM 类型字段不会出现在 CV 类型评测的 payload 中（Pydantic v2 自动排除未设置的可选字段）
        self.assertNotIn("dataset_id", actual_payload)
        self.assertNotIn("dataset_version_id", actual_payload)
        self.assertNotIn("evaled_artifact_path", actual_payload)
        self.assertNotIn("report", actual_payload)

    def test_create_cv_run_custom_user_id(self):
        """测试创建 CV 类型评测运行 - 自定义 user_id"""
        # 模拟成功的创建响应
        mock_eval_run = {
            "id": 999,
            "name": "cv_eval_custom",
            "description": "CV evaluation custom",
            "user_id": 3750,
            "model_id": 3,
            "model_name": "cv_model_v2",
            "dataset_id": 0,  # 使用默认值而不是 None
            "dataset_version_id": 0,  # 使用默认值而不是 None
            "dataset_name": "",  # 使用空字符串而不是 None
            "status": "created",
            "prediction_artifact_path": "coco_dt.json",
            "evaled_artifact_path": "",  # 使用空字符串而不是 None
            "run_id": "cv_run_999",
            "dataset_summary": {},
            "metrics_summary": {},
            "viz_summary": {},
            "eval_config": None,
            "created_at": 1640995200,
            "updated_at": 1640995200,
        }

        mock_response = {"code": 0, "msg": None, "data": {"eval_run": mock_eval_run}}

        mock_resp = Mock()
        mock_resp.json.return_value = mock_response
        self.http_client.post.return_value = mock_resp

        # 调用方法（提供自定义 user_id）
        result = self.eval_service.create_cv_run(
            run_id="cv_run_999",
            prediction_artifact_path="coco_dt.json",
            metrics_artifact_path="metrics.json",
            ground_truth_artifact_path="coco_gt.json",
            user_id=3750,
        )

        # 验证结果
        self.assertEqual(result, 999)

        # 验证 HTTP 调用
        self.http_client.post.assert_called_once()
        call_args = self.http_client.post.call_args
        actual_payload = call_args[1]["json"]

        # 验证 CV 类型关键字段
        self.assertEqual(actual_payload["type"], "cv")
        self.assertEqual(actual_payload["user_id"], 3750)
        self.assertEqual(actual_payload["run_id"], "cv_run_999")
        self.assertEqual(actual_payload["prediction_artifact_path"], "coco_dt.json")
        self.assertEqual(actual_payload["metrics_artifact_path"], "metrics.json")
        self.assertEqual(actual_payload["ground_truth_artifact_path"], "coco_gt.json")

    def test_create_eval_api_error(self):
        """测试创建评测 - API错误"""
        with patch("aihub.services.dataset_management.DatasetManagementService") as mock_dataset_service_class:
            # 模拟数据集版本
            mock_dataset_version = Mock()
            mock_dataset_version.dataset_id = 1
            mock_dataset_version.id = 1

            mock_dataset_service = Mock()
            mock_dataset_service.get_dataset_version_by_name.return_value = mock_dataset_version
            mock_dataset_service_class.return_value = mock_dataset_service

            # 模拟 API 错误
            mock_response = {"code": 2001, "msg": "Invalid dataset version", "data": None}

            mock_resp = Mock()
            mock_resp.json.return_value = mock_response
            self.http_client.post.return_value = mock_resp

            with self.assertRaises(Exception) as context:
                self.eval_service.create(
                    dataset_version_name="invalid_dataset",
                    prediction_artifact_path="/path/to/prediction.json",
                    evaled_artifact_path="/path/to/evaled.json",
                    report_json={"accuracy": 0.95},
                    run_id="test_run_error",
                )

            self.assertIn("backend code 2001", str(context.exception))
            self.assertIn("Invalid dataset version", str(context.exception))

    def test_create_cv_run_api_error(self):
        """测试创建 CV 评测运行 - API错误"""
        # 模拟 API 错误
        mock_response = {"code": 3001, "msg": "Invalid CV run parameters", "data": None}

        mock_resp = Mock()
        mock_resp.json.return_value = mock_response
        self.http_client.post.return_value = mock_resp

        with self.assertRaises(Exception) as context:
            self.eval_service.create_cv_run(
                run_id="invalid_cv_run",
                prediction_artifact_path="invalid.json",
                metrics_artifact_path="invalid_metrics.json",
                ground_truth_artifact_path="invalid_gt.json",
            )

        self.assertIn("backend code 3001", str(context.exception))
        self.assertIn("Invalid CV run parameters", str(context.exception))

    def test_create_face_reid_run_default_user_id(self):
        """测试创建 Face ReID 类型评测运行 - 使用默认 user_id"""
        # 模拟成功的创建响应
        mock_eval_run = {
            "id": 888,
            "name": "face_reid_eval",
            "description": "Face ReID evaluation",
            "user_id": 0,
            "model_id": 1,
            "model_name": "face_recognition_model",
            "dataset_id": 10,
            "dataset_version_id": 1,
            "dataset_name": "GalleryDataset",
            "status": "running",
            "prediction_artifact_path": "path/to/predictions.jsonl",
            "evaled_artifact_path": "",
            "run_id": "face_run_123",
            "dataset_summary": {},
            "metrics_summary": {},
            "viz_summary": {},
            "eval_config": None,
            "created_at": 1640995200,
            "updated_at": 1640995200,
        }

        mock_response = {"code": 0, "msg": None, "data": {"eval_run": mock_eval_run}}

        mock_resp = Mock()
        mock_resp.json.return_value = mock_response
        self.http_client.post.return_value = mock_resp

        # 准备指标产物配置
        metrics_viz_artifacts = [
            MetricsArtifact(MetricVizConfigID=1, MetricArtifactPath="path/to/metrics1.csv"),
            MetricsArtifact(MetricVizConfigID=2, MetricArtifactPath="path/to/metrics2.csv"),
        ]

        # 调用方法（不提供 user_id，使用默认值）
        result = self.eval_service.create_face_reid_run(
            run_id="face_run_123",
            model_id=1,
            prediction_artifact_path="path/to/predictions.jsonl",
            gallery_dataset_id=10,
            gallery_dataset_version_id=1,
            query_dataset_id=11,
            query_dataset_version_id=1,
            id_dataset_id=12,
            id_dataset_version_id=1,
            metrics_viz_artifacts=metrics_viz_artifacts,
            search_result_artifact_path="path/to/search_results.jsonl",
            metrics_artifact_path="path/to/metrics.json",
        )

        # 验证结果
        self.assertEqual(result, 888)

        # 验证 HTTP 调用
        self.http_client.post.assert_called_once()
        call_args = self.http_client.post.call_args
        actual_payload = call_args[1]["json"]

        # 验证 Face ReID 类型必需字段
        self.assertEqual(actual_payload["type"], "face")
        self.assertEqual(actual_payload["user_id"], 0)
        self.assertEqual(actual_payload["run_id"], "face_run_123")
        self.assertEqual(actual_payload["model_id"], 1)
        self.assertEqual(actual_payload["prediction_artifact_path"], "path/to/predictions.jsonl")

        # 验证 face_reid_config
        self.assertIn("face_reid_config", actual_payload)
        face_reid_config = actual_payload["face_reid_config"]
        self.assertEqual(face_reid_config["gallery_dataset_id"], 10)
        self.assertEqual(face_reid_config["gallery_dataset_version_id"], 1)
        self.assertEqual(face_reid_config["query_dataset_id"], 11)
        self.assertEqual(face_reid_config["query_dataset_version_id"], 1)
        self.assertEqual(face_reid_config["id_dataset_id"], 12)
        self.assertEqual(face_reid_config["id_dataset_version_id"], 1)
        self.assertEqual(face_reid_config["search_result_artifact_path"], "path/to/search_results.jsonl")

        # 验证 metrics_viz_artifacts
        self.assertEqual(len(face_reid_config["metrics_viz_artifacts"]), 2)
        self.assertEqual(face_reid_config["metrics_viz_artifacts"][0]["MetricVizConfigID"], 1)
        self.assertEqual(face_reid_config["metrics_viz_artifacts"][0]["MetricArtifactPath"], "path/to/metrics1.csv")
        self.assertEqual(face_reid_config["metrics_viz_artifacts"][1]["MetricVizConfigID"], 2)
        self.assertEqual(face_reid_config["metrics_viz_artifacts"][1]["MetricArtifactPath"], "path/to/metrics2.csv")

    def test_create_face_reid_run_custom_user_id(self):
        """测试创建 Face ReID 类型评测运行 - 自定义 user_id"""
        # 模拟成功的创建响应
        mock_eval_run = {
            "id": 777,
            "name": "face_reid_eval_custom",
            "description": "Face ReID evaluation custom",
            "user_id": 3750,
            "model_id": 2,
            "model_name": "face_recognition_model_v2",
            "dataset_id": 20,
            "dataset_version_id": 2,
            "dataset_name": "GalleryDatasetV2",
            "status": "running",
            "prediction_artifact_path": "path/to/predictions_v2.jsonl",
            "evaled_artifact_path": "",
            "run_id": "face_run_456",
            "dataset_summary": {},
            "metrics_summary": {},
            "viz_summary": {},
            "eval_config": None,
            "created_at": 1640995200,
            "updated_at": 1640995200,
        }

        mock_response = {"code": 0, "msg": None, "data": {"eval_run": mock_eval_run}}

        mock_resp = Mock()
        mock_resp.json.return_value = mock_response
        self.http_client.post.return_value = mock_resp

        # 准备指标产物配置
        metrics_viz_artifacts = [MetricsArtifact(MetricVizConfigID=3, MetricArtifactPath="path/to/metrics3.csv")]

        # 调用方法（提供自定义 user_id）
        result = self.eval_service.create_face_reid_run(
            run_id="face_run_456",
            model_id=2,
            prediction_artifact_path="path/to/predictions_v2.jsonl",
            gallery_dataset_id=20,
            gallery_dataset_version_id=2,
            query_dataset_id=21,
            query_dataset_version_id=2,
            id_dataset_id=22,
            id_dataset_version_id=2,
            metrics_viz_artifacts=metrics_viz_artifacts,
            search_result_artifact_path="path/to/search_results_v2.jsonl",
            metrics_artifact_path="path/to/metrics_v2.json",
            user_id=3750,
        )

        # 验证结果
        self.assertEqual(result, 777)

        # 验证 HTTP 调用
        self.http_client.post.assert_called_once()
        call_args = self.http_client.post.call_args
        actual_payload = call_args[1]["json"]

        # 验证 Face ReID 类型关键字段
        self.assertEqual(actual_payload["type"], "face")
        self.assertEqual(actual_payload["user_id"], 3750)
        self.assertEqual(actual_payload["run_id"], "face_run_456")
        self.assertEqual(actual_payload["model_id"], 2)

        # 验证 face_reid_config
        face_reid_config = actual_payload["face_reid_config"]
        self.assertEqual(face_reid_config["gallery_dataset_id"], 20)
        self.assertEqual(face_reid_config["gallery_dataset_version_id"], 2)
        self.assertEqual(len(face_reid_config["metrics_viz_artifacts"]), 1)

    def test_create_face_reid_run_api_error(self):
        """测试创建 Face ReID 评测运行 - API错误"""
        # 模拟 API 错误
        mock_response = {"code": 4001, "msg": "Invalid Face ReID configuration", "data": None}

        mock_resp = Mock()
        mock_resp.json.return_value = mock_response
        self.http_client.post.return_value = mock_resp

        metrics_viz_artifacts = [MetricsArtifact(MetricVizConfigID=1, MetricArtifactPath="path/to/metrics1.csv")]

        with self.assertRaises(Exception) as context:
            self.eval_service.create_face_reid_run(
                run_id="invalid_face_run",
                model_id=999,
                prediction_artifact_path="invalid.jsonl",
                gallery_dataset_id=99,
                gallery_dataset_version_id=99,
                query_dataset_id=99,
                query_dataset_version_id=99,
                id_dataset_id=99,
                id_dataset_version_id=99,
                metrics_viz_artifacts=metrics_viz_artifacts,
                search_result_artifact_path="invalid_search.jsonl",
                metrics_artifact_path="invalid_metrics.json",
            )

        self.assertIn("backend code 4001", str(context.exception))
        self.assertIn("Invalid Face ReID configuration", str(context.exception))


if __name__ == "__main__":
    unittest.main()


class TestEvalService(unittest.TestCase):

    def test_create_performance_run_e2e(self):
        """性能评测端到端（无Mock）：上传制品 → 创建任务 → 列表验证"""
        client = Client(base_url=BASE_URL, token=TOKEN)

        model_name = os.getenv("AIHUB_TEST_MODEL_NAME", "我的测试模型")
        task_name = "perf-" + model_name

        # 检查模型是否存在（不存在则跳过此集成用例）
        try:
            model_item = client.model_center.get_model_db(name=model_name)
        except Exception as e:
            self.skipTest(f"模型 '{model_name}' 不存在或服务不可用: {e}")

        # 准备并上传性能指标制品
        local_metrics = os.path.abspath("./perf_metrics.json")
        metrics_content = {
            "info": {"model_name": model_name, "note": "integration test"},
            "report": [{"batch_size": 32, "latency_ms": 12.3, "throughput_qps": 345.6}],
        }
        with open(local_metrics, "w", encoding="utf-8") as f:
            json.dump(metrics_content, f)

        artifact_path = f"metrics.json"
        client.artifact.create_artifact(
            local_path=local_metrics,
            artifact_path=artifact_path,
            artifact_type=ArtifactType.metrics,
        )

        client.eval.create_performance_run(
            model_name=model_name,
            eval_name=task_name,
            benchmark_artifact_path=artifact_path,
            eval_config={"hardware": "A100", "framework": "onnxruntime", "precision": "fp16"},
            is_public=True,
            benchmark_report=[
                {"batch_size": 32, "latency_ms": 12.3, "throughput_qps": 345.6, "device": "GPU"},
                {"batch_size": 32, "latency_ms": 12.3, "throughput_qps": 345.6, "device": "CPU"},
                {"batch_size": 32, "latency_ms": 12.3, "throughput_qps": 345.6, "device": "IPU"},
                {"batch_size": 32, "latency_ms": 12.3, "throughput_qps": 345.6, "device": "FPGA"},
                {"batch_size": 32, "latency_ms": 12.3, "throughput_qps": 345.6, "device": "ASIC"},
                {"batch_size": 32, "latency_ms": 12.3, "throughput_qps": 345.6, "device": "Other"},
            ],
            access_user_ids=[],
        )
