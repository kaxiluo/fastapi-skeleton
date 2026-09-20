from datetime import datetime
from types import UnionType
from typing import Union, get_args, get_origin

from pydantic import BaseModel, ConfigDict, model_serializer

from app.utils.timezone_utils import format_datetime


def _is_datetime_annotation(annotation) -> bool:
    if annotation is datetime:
        return True
    origin = get_origin(annotation)
    if origin is Union or origin is UnionType:
        return datetime in get_args(annotation)
    return False


class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    # json 模式下 handler 已把 datetime 转成 ISO 字符串，无法事后识别，
    # 因此按 model_fields 注解定位 datetime 字段，从实例取原始值统一格式化
    @model_serializer(mode="wrap", when_used="json")
    def _serialize_datetimes(self, handler, info):
        data = handler(self)
        for name, field in type(self).model_fields.items():
            if not _is_datetime_annotation(field.annotation):
                continue
            key = field.alias if (info.by_alias and field.alias) else name
            if key in data:
                data[key] = format_datetime(getattr(self, name, None))
        return data
