# Copyright 2023 Baidu, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file
# except in compliance with the License. You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the
# License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied. See the License for the specific language governing permissions
# and limitations under the License.
"""
This module provide schema.
"""
import base64
from typing import Dict, List, Union
from pymochow.model.enum import (
    IndexType,
    AutoBuildPolicyType,
    InvertedIndexAnalyzer,
    InvertedIndexParseMode,
    InvertedIndexFieldAttribute,
    IndexStructureType
)


class AutoBuildTiming:
    """
    AutoBuildTiming
    """

    def __init__(self, timing):
        self._timing = timing
        self._auto_build_policy_type = AutoBuildPolicyType.TIMING

    def to_dict(self):
        """to dict"""
        res = {"policyType": self._auto_build_policy_type, "timing": self._timing}
        return res


class AutoBuildPeriodical:
    """
    AutoBuildPeriodical
    """

    def __init__(self, period_s, timing=""):
        """
        __init__
        """
        self._period_s = period_s
        self._auto_build_policy_type = AutoBuildPolicyType.PERIODICAL
        self._timing = timing

    def to_dict(self):
        """to dict"""
        res = {
            "policyType": self._auto_build_policy_type,
            "periodInSecond": self._period_s,
        }
        if self._timing != "":
            res["timing"] = self._timing
        return res


class AutoBuildRowCountIncrement:
    """
    AutoBuildRowCountIncrement
    """

    def __init__(self, row_count_increment=0, row_count_increment_ratio=0):
        self._row_count_increment = row_count_increment
        self._row_count_increment_ratio = row_count_increment_ratio
        self._auto_build_policy_type = AutoBuildPolicyType.ROW_COUNT_INCREMENT

    def to_dict(self):
        """to dict"""
        res = {
            "policyType": self._auto_build_policy_type,
        }
        if self._row_count_increment != 0:
            res["rowCountIncrement"] = self._row_count_increment
        if self._row_count_increment_ratio != 0:
            res["rowCountIncrementRatio"] = self._row_count_increment_ratio
        return res


class AutoBuildTool:
    """
    AutoBuildTool
    """

    def get_auto_build_index_policy(auto_build_policy_dict):
        """get auto build index policy"""
        if "policyType" not in auto_build_policy_dict:
            return None
        if (auto_build_policy_dict["policyType"].upper() == AutoBuildPolicyType.TIMING.name):
            return AutoBuildTiming(auto_build_policy_dict["timing"])
        elif (auto_build_policy_dict["policyType"].upper() == AutoBuildPolicyType.PERIODICAL.name):
            if "timing" in auto_build_policy_dict:
                return AutoBuildPeriodical(auto_build_policy_dict["periodInSecond"], auto_build_policy_dict["timing"])
            else:
                return AutoBuildPeriodical(auto_build_policy_dict["periodInSecond"])
        elif (auto_build_policy_dict["policyType"].upper() == AutoBuildPolicyType.ROW_COUNT_INCREMENT.name):
            row_count_increment = 0
            row_count_increment_ratio = 0.0
            if "rowCountIncrementRatio" in auto_build_policy_dict:
                row_count_increment_ratio = auto_build_policy_dict["rowCountIncrementRatio"]
            if "rowCountIncrement" in auto_build_policy_dict:
                row_count_increment = auto_build_policy_dict["rowCountIncrement"]
            return AutoBuildRowCountIncrement(row_count_increment, row_count_increment_ratio)

DefaultAutoBuildPeriodical = 24 * 3600
DefaultAutoBuildPolicy = AutoBuildPeriodical(DefaultAutoBuildPeriodical)

class Field:
    """field"""

    def __init__(self,
            field_name,
            field_type,
            primary_key=False,
            partition_key=False,
            auto_increment=False,
            not_null=False,
            dimension=0,
            element_type=None,
            max_capacity=None,
            key_type=None,
            value_type=None):
        """
        - 'dimension' is for FLOAT_VECTOR
        - 'element_type' and 'max_capacity' is for ARRAY
        - 'key_type' and 'value_type' is for MAP
        """
        self._field_name = field_name
        self._field_type = field_type
        self._primary_key = primary_key
        self._partition_key = partition_key
        self._auto_increment = auto_increment
        self._not_null = not_null
        self._dimension = dimension
        self._element_type = element_type
        self._max_capacity = max_capacity
        self._key_type = key_type
        self._value_type = value_type

    @property
    def field_name(self):
        """field name"""
        return self._field_name

    @property
    def field_type(self):
        """field type"""
        return self._field_type

    @property
    def primary_key(self):
        """primary key"""
        return self._primary_key

    @property
    def partition_key(self):
        """partition key"""
        return self._partition_key

    @property
    def auto_increment(self):
        """auto increment"""
        return self._auto_increment

    @property
    def not_null(self):
        """not null"""
        return self._not_null

    @property
    def dimension(self):
        """dimension"""
        return self._dimension

    @property
    def element_type(self):
        """element type"""
        return self._element_type

    @property
    def max_capacity(self):
        """max capacity"""
        return self._max_capacity

    @property
    def key_type(self):
        """key type"""
        return self._key_type

    @property
    def value_type(self):
        """value type"""
        return self._value_type

    def to_dict(self):
        """to dict"""
        res = {
            "fieldName": self.field_name,
            "fieldType": self.field_type,
            "notNull": self.not_null
        }
        if self.primary_key:
            res["primaryKey"] = True
        if self.partition_key:
            res["partitionKey"] = True
        if self.auto_increment:
            res["autoIncrement"] = True
        if self.dimension > 0:
            res["dimension"] = self.dimension
        if self.element_type is not None:
            res["elementType"] = self.element_type
        if self.max_capacity is not None:
            res["maxCapacity"] = self.max_capacity
        if self._key_type is not None:
            res["keyType"] = self.key_type
        if self._value_type is not None:
            res["valueType"] = self._value_type
        return res


class IndexField:
    """index field"""

    def __init__(self, index_name, field, index_type):
        self._index_name = index_name
        self._field = field
        self._index_type = index_type

    @property
    def index_type(self):
        """index type"""
        return self._index_type

    @property
    def index_name(self):
        """index name"""
        return self._index_name

    @property
    def field(self):
        """field"""
        return self._field


class HNSWParams:
    """
    The hnsw vector index params.
    """

    def __init__(self, m: int, efconstruction: int) -> None:
        self.m = m
        self.ef_construction = efconstruction

    def to_dict(self):
        """to dict"""
        res = {
            "M": self.m,
            "efConstruction": self.ef_construction
        }
        return res


class HNSWPQParams:
    """
    The hnsw pq vector index params.
    """

    def __init__(self, m: int, efconstruction: int, NSQ: int, samplerate: float) -> None:
        self.m = m
        self.ef_construction = efconstruction
        self.NSQ = NSQ
        self.samplerate = samplerate
    
    def to_dict(self):
        """to dict"""
        res = {
            "M": self.m,
            "efConstruction": self.ef_construction,
            "NSQ": self.NSQ,
            "sampleRate": self.samplerate
        }
        return res


class DISKANNParams:
    """
    The diskann vector index params.
    """

    def __init__(self, NSQ: int, R: int, L: int) -> None:
        self.NSQ = NSQ
        self.R = R
        self.L = L

    def to_dict(self):
        """to dict"""
        res = {
            "NSQ": self.NSQ,
            "R": self.R,
            "L": self.L
        }
        return res


class HNSWSQParams:
    """
    The hnsw sq vector index params.
    """

    def __init__(self, m: int, efconstruction: int, qtBits: int) -> None:
        self.m = m
        self.ef_construction = efconstruction
        self.qtBits = qtBits
    
    def to_dict(self):
        """to dict"""
        res = {
            "M": self.m,
            "efConstruction": self.ef_construction,
            "qtBits": self.qtBits
        }
        return res


class PUCKParams:
    """
    The puck vector index params.
    """

    def __init__(self, coarseClusterCount: int, fineClusterCount: int) -> None:
        self.coarseClusterCount = coarseClusterCount
        self.fineClusterCount = fineClusterCount

    def to_dict(self):
        """to dict"""
        res = {
            "coarseClusterCount": self.coarseClusterCount,
            "fineClusterCount": self.fineClusterCount
        }
        return res


class IVFParams:
    """
    The ivf vector index params.
    """

    def __init__(self, nlist: int) -> None:
        self.nlist = nlist

    def to_dict(self):
        """to dict"""
        res = {
            "nlist": self.nlist
        }
        return res


class IVFSQParams:
    """
    The ivfsq vector index params.
    """

    def __init__(self, nlist: int, qtBits: int) -> None:
        self.nlist = nlist
        self.qtBits = qtBits

    def to_dict(self):
        """to dict"""
        res = {
            "nlist": self.nlist,
            "qtBits": self.qtBits
        }
        return res


class VectorIndex(IndexField):
    """
    Args:
        index_name(str): The field name of the index.
        field(str): make index on which field
        metric_type(MetricType): The metric type of the vector index.
        params(Any): HNSWParams if the index_type is HNSW
        auto_build(boolean): auto build vector index
    """
    def __init__(
            self,
            index_name,
            index_type,
            field,
            metric_type,
            params=None,
            auto_build=False,
            auto_build_index_policy=None,
            **kwargs):
        super().__init__(index_name=index_name, index_type=index_type, field=field)
        self._metric_type = metric_type
        self._params = params
        self._auto_build = auto_build
        if self._auto_build:
            self._auto_build_index_policy = auto_build_index_policy
        else:
            self._auto_build_index_policy = None
        self._state = kwargs.get('state', None)

    @property
    def metric_type(self):
        """metric type"""
        return self._metric_type

    @property
    def params(self):
        """params"""
        return self._params

    @property
    def auto_build(self):
        """auto build"""
        return self._auto_build

    @property
    def state(self):
        """state"""
        return self._state
    @property
    def auto_build_index_policy(self):
        """state"""
        return self._auto_build_index_policy

    def to_dict(self):
        """to dict"""
        res = {
            "indexName": self.index_name,
            "indexType": self.index_type,
            "field": self.field,
            "metricType": self.metric_type,
            "autoBuild": self.auto_build
        }
        if self.params is not None:
            res["params"] = self.params.to_dict()
        if self.state is not None:
            res["state"] = self.state
        if self.auto_build_index_policy is not None:
            res["autoBuildPolicy"] = self.auto_build_index_policy.to_dict()
        return res


class SecondaryIndex(IndexField):
    """secondary index"""

    def __init__(
            self,
            index_name,
            field):
        super().__init__(index_name=index_name, index_type=IndexType.SECONDARY_INDEX,
                field=field)

    def to_dict(self):
        """to dict"""
        res = {
            "indexName": self.index_name,
            "indexType": self.index_type,
            "field": self.field
        }
        return res

class FilteringIndex(IndexField):
    """filtering index"""

    def __init__(
            self,
            index_name: str,
            fields: Union[List[str], List[Dict[str, str]]]):
        """init

        FilteringIndex 用于在 create_table 时，为 'fields' 指定的列建立FILTERING索引。

        """
        super().__init__(index_name=index_name,
                         field=None,
                         index_type=IndexType.FILTERING_INDEX)
        self._fields = fields

    @classmethod
    def from_dict_list(cls,
                       index_name: str,
                       fields: List[Dict[str, str]]):
        """
        create FilteringIndex instance from dict list
        """
        return cls(index_name, fields)

    @classmethod
    def from_list(cls,
                  index_name: str,
                  fields: List[str]):
        """
        create FilteringIndex instance from list
        """
        return cls(index_name, fields)

    def to_dict(self):
        """to dict"""
        fields_dict_list = []
        for field in self._fields:
            if isinstance(field, str):
                field_dict = {
                    "field": field
                }
                fields_dict_list.append(field_dict)
            elif isinstance(field, dict):
                fields_dict_list.append(field)
        res = {
            "indexName": self.index_name,
            "indexType": self.index_type,
            "fields": fields_dict_list
        }
        return res


class InvertedIndexParams:
    """
    inverted index params.
    """

    def __init__(
            self,
            analyzer: InvertedIndexAnalyzer = None,
            parse_mode: InvertedIndexParseMode = None,
            case_sensitive: bool = True):
        """init"""
        self._params = {}
        if analyzer is not None:
            self._params["analyzer"] = analyzer
        if parse_mode is not None:
            self._params["parseMode"] = parse_mode

        self._params["analyzerCaseSensitive"] = case_sensitive

    def to_dict(self) -> Dict[str, str]:
        """to dict"""
        return self._params


class InvertedIndex(IndexField):
    """inverted index (for BM25 search)"""
    def __init__(
            self,
            index_name: str,
            fields: List[str],
            params: InvertedIndexParams,
            field_attributes: List[InvertedIndexFieldAttribute] = []):
        """init

        InvertedIndex 用于在 create_table 时，为 'fields' 指定的列建立
        倒排索引。注意 fields 中包含的列应当是 TEXT、TEXT_GBK 或者
        TEXT_GB18030 类型，否则 create_table 会失败。

        'attributes' 可以为空, 否则, 应当与 fields 有相同数量的元素

        """
        super().__init__(index_name=index_name,
                         field=None,
                         index_type=IndexType.INVERTED_INDEX)
        self._fields = fields
        self._field_attributes = field_attributes
        self._params = params

    def to_dict(self):
        """to dict"""
        res = {
            "indexName": self.index_name,
            "indexType": self.index_type,
            "fields": self._fields,
            "params": self._params.to_dict()
        }
        if len(self._field_attributes) != 0:
            res["fieldsIndexAttributes"] = self._field_attributes
        return res


class Schema:
    """schema"""

    def __init__(self, fields, indexes=None):
        self._fields = fields
        self._indexes = indexes

    @property
    def indexes(self):
        """indexes"""
        return self._indexes

    @property
    def fields(self):
        """fields"""
        return self._fields

    def to_dict(self):
        """to dict"""
        res = {}
        res["fields"] = []
        for field in self.fields:
            res["fields"].append(field.to_dict())

        if self.indexes is not None:
            res["indexes"] = []
            for index in self.indexes:
                res["indexes"].append(index.to_dict())
        return res


class FusionRankPolicy:
    '''concrete impletations are RRFRank and WeightedRank'''


class RRFRank(FusionRankPolicy):
    def __init__(self, k: int):
        self._k = k

    def to_dict(self):
        return {
            "strategy": "rrf",
            "params": {
                "k": self._k
            }
        }


class WeightedRank(FusionRankPolicy):
    def __init__(self, weights: List[float]):
        self._weights = weights

    def to_dict(self):
        return {
            "strategy": "ws",
            "params": {
                "weights": self._weights
            }
        }
