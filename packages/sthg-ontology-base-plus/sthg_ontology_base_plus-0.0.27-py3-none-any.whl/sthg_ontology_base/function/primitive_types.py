from typing import Any, Dict, Optional, Union
from datetime import datetime, date
from decimal import Decimal as PyDecimal
import base64
import mimetypes
from pathlib import Path
from io import BytesIO
from .base import PalantirType, ValidationError, validate_type, safe_json_serialize


class Boolean(PalantirType[bool]):
    """布尔类型"""

    def _validate(self, value: Any) -> bool:
        if isinstance(value, bool):
            return value
        elif isinstance(value, str):
            if value.lower() in ('true', '1', 'yes', 'on'):
                return True
            elif value.lower() in ('false', '0', 'no', 'off'):
                return False
            else:
                raise ValidationError(f"Invalid boolean string: {value}")
        elif isinstance(value, (int, float)):
            return bool(value)
        else:
            raise ValidationError(f"Cannot convert {type(value).__name__} to Boolean")

    def to_json(self) -> Dict[str, Any]:
        return {
            "type": "Boolean",
            "value": self._value
        }

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> 'Boolean':
        return cls(data.get("value"))

    @classmethod
    def type_name(cls) -> str:
        return "Boolean"


class String(PalantirType[str]):
    """字符串类型"""

    def _validate(self, value: Any) -> str:
        if value is None:
            return ""
        return str(value)

    def to_json(self) -> Dict[str, Any]:
        return {
            "type": "String",
            "value": self._value
        }

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> 'String':
        return cls(data.get("value"))

    @classmethod
    def type_name(cls) -> str:
        return "String"


class Integer(PalantirType[int]):
    """整数类型"""

    def _validate(self, value: Any) -> int:
        if isinstance(value, bool):
            raise ValidationError("Boolean cannot be converted to Integer")
        elif isinstance(value, int):
            return value
        elif isinstance(value, float):
            if value.is_integer():
                return int(value)
            else:
                raise ValidationError(f"Float {value} is not a whole number")
        elif isinstance(value, str):
            try:
                return int(value)
            except ValueError:
                raise ValidationError(f"Cannot convert string '{value}' to Integer")
        else:
            raise ValidationError(f"Cannot convert {type(value).__name__} to Integer")

    def to_json(self) -> Dict[str, Any]:
        return {
            "type": "Integer",
            "value": self._value
        }

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> 'Integer':
        return cls(data.get("value"))

    @classmethod
    def type_name(cls) -> str:
        return "Integer"


class Long(PalantirType[int]):
    """长整数类型（在Python中与Integer相同）"""

    def _validate(self, value: Any) -> int:
        if isinstance(value, bool):
            raise ValidationError("Boolean cannot be converted to Long")
        elif isinstance(value, int):
            return value
        elif isinstance(value, float):
            if value.is_integer():
                return int(value)
            else:
                raise ValidationError(f"Float {value} is not a whole number")
        elif isinstance(value, str):
            try:
                return int(value)
            except ValueError:
                raise ValidationError(f"Cannot convert string '{value}' to Long")
        else:
            raise ValidationError(f"Cannot convert {type(value).__name__} to Long")

    def to_json(self) -> Dict[str, Any]:
        return {
            "type": "Long",
            "value": self._value
        }

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> 'Long':
        return cls(data.get("value"))

    @classmethod
    def type_name(cls) -> str:
        return "Long"


class Float(PalantirType[float]):
    """单精度浮点数类型"""

    def _validate(self, value: Any) -> float:
        if isinstance(value, bool):
            raise ValidationError("Boolean cannot be converted to Float")
        elif isinstance(value, (int, float)):
            return float(value)
        elif isinstance(value, str):
            try:
                return float(value)
            except ValueError:
                raise ValidationError(f"Cannot convert string '{value}' to Float")
        elif isinstance(value, Decimal):
            return float(value)
        else:
            raise ValidationError(f"Cannot convert {type(value).__name__} to Float")

    def to_json(self) -> Dict[str, Any]:
        return {
            "type": "Float",
            "value": self._value
        }

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> 'Float':
        return cls(data.get("value"))

    @classmethod
    def type_name(cls) -> str:
        return "Float"


class Double(PalantirType[float]):
    """双精度浮点数类型（在Python中与Float相同）"""

    def _validate(self, value: Any) -> float:
        if isinstance(value, bool):
            raise ValidationError("Boolean cannot be converted to Double")
        elif isinstance(value, (int, float)):
            return float(value)
        elif isinstance(value, str):
            try:
                return float(value)
            except ValueError:
                raise ValidationError(f"Cannot convert string '{value}' to Double")
        elif isinstance(value, Decimal):
            return float(value)
        else:
            raise ValidationError(f"Cannot convert {type(value).__name__} to Double")

    def to_json(self) -> Dict[str, Any]:
        return {
            "type": "Double",
            "value": self._value
        }

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> 'Double':
        return cls(data.get("value"))

    @classmethod
    def type_name(cls) -> str:
        return "Double"


class Date(PalantirType[date]):
    """日期类型"""

    def _validate(self, value: Any) -> date:
        if isinstance(value, date):
            if isinstance(value, datetime):
                return value.date()
            return value
        elif isinstance(value, str):
            try:
                # 尝试解析ISO格式日期
                if 'T' in value or ' ' in value:
                    return datetime.fromisoformat(value.replace('Z', '+00:00')).date()
                else:
                    return datetime.strptime(value, '%Y-%m-%d').date()
            except ValueError:
                raise ValidationError(f"Cannot parse date string '{value}'")
        else:
            raise ValidationError(f"Cannot convert {type(value).__name__} to Date")

    def to_json(self) -> Dict[str, Any]:
        return {
            "type": "Date",
            "value": self._value.isoformat() if self._value else None
        }

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> 'Date':
        value = data.get("value")
        if value:
            return cls(value)
        return cls()

    @classmethod
    def type_name(cls) -> str:
        return "Date"


class Timestamp(PalantirType[datetime]):
    """时间戳类型"""

    def _validate(self, value: Any) -> datetime:
        if isinstance(value, datetime):
            return value
        elif isinstance(value, date):
            return datetime.combine(value, datetime.min.time())
        elif isinstance(value, str):
            try:
                return datetime.fromisoformat(value.replace('Z', '+00:00'))
            except ValueError:
                raise ValidationError(f"Cannot parse timestamp string '{value}'")
        elif isinstance(value, (int, float)):
            return datetime.fromtimestamp(value)
        else:
            raise ValidationError(f"Cannot convert {type(value).__name__} to Timestamp")

    def to_json(self) -> Dict[str, Any]:
        return {
            "type": "Timestamp",
            "value": self._value.isoformat() if self._value else None
        }

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> 'Timestamp':
        value = data.get("value")
        if value:
            return cls(value)
        return cls()

    @classmethod
    def type_name(cls) -> str:
        return "Timestamp"


class Binary(PalantirType[bytes]):
    """二进制数据类型"""

    def _validate(self, value: Any) -> bytes:
        if isinstance(value, bytes):
            return value
        elif isinstance(value, str):
            try:
                import base64
                return base64.b64decode(value)
            except Exception:
                return value.encode('utf-8')
        elif isinstance(value, (list, tuple)):
            return bytes(value)
        else:
            raise ValidationError(f"Cannot convert {type(value).__name__} to Binary")

    def to_json(self) -> Dict[str, Any]:
        import base64
        return {
            "type": "Binary",
            "value": base64.b64encode(self._value).decode('utf-8') if self._value else None
        }

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> 'Binary':
        value = data.get("value")
        if value:
            return cls(value)
        return cls()

    @classmethod
    def type_name(cls) -> str:
        return "Binary"


class Attachment(PalantirType[Dict[str, Any]]):


    def __init__(self, filename: str = None, content: bytes = None,
                 content_type: str = None, size: int = None):
        attachment_data = {
            'filename': filename,
            'content': content,
            'content_type': content_type or self._guess_content_type(filename),
            'size': size or (len(content) if content else 0)
        }
        super().__init__(attachment_data)

    def _guess_content_type(self, filename: str) -> str:
        """根据文件名猜测内容类型"""
        if not filename:
            return 'application/octet-stream'
        return mimetypes.guess_type(filename)[0] or 'application/octet-stream'

    def _validate(self, value: Any) -> Dict[str, Any]:
        if isinstance(value, dict):
            filename = value.get('filename')
            content = value.get('content')
            content_type = value.get('content_type')
            size = value.get('size')
        elif isinstance(value, str):
            # 如果是字符串，当作文件路径处理
            path = Path(value)
            if path.exists():
                filename = path.name
                content = path.read_bytes()
                content_type = self._guess_content_type(filename)
                size = len(content)
            else:
                raise ValidationError(f"File not found: {value}")
        else:
            raise ValidationError(f"Attachment expects dict or file path, got {type(value).__name__}")

        # 验证文件名
        if filename and not isinstance(filename, str):
            filename = str(filename)

        # 验证内容
        if content is not None and not isinstance(content, bytes):
            if isinstance(content, str):
                content = content.encode('utf-8')
            else:
                raise ValidationError(f"Attachment content must be bytes, got {type(content).__name__}")

        # 验证内容类型
        if content_type and not isinstance(content_type, str):
            content_type = str(content_type)

        # 验证大小
        if size is not None:
            if not isinstance(size, int):
                try:
                    size = int(size)
                except (ValueError, TypeError):
                    raise ValidationError(f"Attachment size must be integer, got {type(size).__name__}")
            if size < 0:
                raise ValidationError("Attachment size cannot be negative")

        return {
            'filename': filename,
            'content': content,
            'content_type': content_type or 'application/octet-stream',
            'size': size or (len(content) if content else 0)
        }

    @property
    def filename(self) -> Optional[str]:
        return self._value.get('filename')

    @property
    def content(self) -> Optional[bytes]:
        return self._value.get('content')

    @property
    def content_type(self) -> str:
        return self._value.get('content_type', 'application/octet-stream')

    @property
    def size(self) -> int:
        return self._value.get('size', 0)

    def save_to_file(self, path: Union[str, Path]):
        """保存附件到文件"""
        if not self.content:
            raise ValidationError("No content to save")

        path = Path(path)
        if path.is_dir():
            if not self.filename:
                raise ValidationError("No filename specified")
            path = path / self.filename

        path.write_bytes(self.content)

    def read(self) -> BytesIO:
        """返回文件内容的BytesIO对象，支持.getvalue()方法"""
        content = self.content or b''
        return BytesIO(content)

    def to_json(self) -> Dict[str, Any]:
        return {
            "type": "Attachment",
            "value": {
                "filename": self.filename,
                "content": base64.b64encode(self.content).decode('utf-8') if self.content else None,
                "contentType": self.content_type,
                "size": self.size
            }
        }

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> 'Attachment':
        value = data.get("value", {})
        content_b64 = value.get("content")
        content = base64.b64decode(content_b64) if content_b64 else None

        return cls(
            filename=value.get("filename"),
            content=content,
            content_type=value.get("contentType"),
            size=value.get("size")
        )

    @classmethod
    def type_name(cls) -> str:
        return "Attachment"

    def __str__(self) -> str:
        return f"Attachment(filename={self.filename}, size={self.size}, type={self.content_type})"


class Byte(PalantirType[int]):
    """字节类型，8位有符号整数（-128到127）"""

    def _validate(self, value: Any) -> int:
        if isinstance(value, bool):
            raise ValidationError("Boolean cannot be converted to Byte")
        elif isinstance(value, int):
            if -128 <= value <= 127:
                return value
            else:
                raise ValidationError(f"Byte value {value} out of range (-128 to 127)")
        elif isinstance(value, float):
            if value.is_integer():
                int_val = int(value)
                if -128 <= int_val <= 127:
                    return int_val
                else:
                    raise ValidationError(f"Byte value {int_val} out of range (-128 to 127)")
            else:
                raise ValidationError(f"Float {value} is not a whole number")
        elif isinstance(value, str):
            try:
                int_val = int(value)
                if -128 <= int_val <= 127:
                    return int_val
                else:
                    raise ValidationError(f"Byte value {int_val} out of range (-128 to 127)")
            except ValueError:
                raise ValidationError(f"Cannot convert string '{value}' to Byte")
        else:
            raise ValidationError(f"Cannot convert {type(value).__name__} to Byte")

    def to_json(self) -> Dict[str, Any]:
        return {
            "type": "Byte",
            "value": self._value
        }

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> 'Byte':
        return cls(data.get("value"))

    @classmethod
    def type_name(cls) -> str:
        return "Byte"


class Short(PalantirType[int]):
    """短整数类型，16位有符号整数（-32768到32767）"""

    def _validate(self, value: Any) -> int:
        if isinstance(value, bool):
            raise ValidationError("Boolean cannot be converted to Short")
        elif isinstance(value, int):
            if -32768 <= value <= 32767:
                return value
            else:
                raise ValidationError(f"Short value {value} out of range (-32768 to 32767)")
        elif isinstance(value, float):
            if value.is_integer():
                int_val = int(value)
                if -32768 <= int_val <= 32767:
                    return int_val
                else:
                    raise ValidationError(f"Short value {int_val} out of range (-32768 to 32767)")
            else:
                raise ValidationError(f"Float {value} is not a whole number")
        elif isinstance(value, str):
            try:
                int_val = int(value)
                if -32768 <= int_val <= 32767:
                    return int_val
                else:
                    raise ValidationError(f"Short value {int_val} out of range (-32768 to 32767)")
            except ValueError:
                raise ValidationError(f"Cannot convert string '{value}' to Short")
        else:
            raise ValidationError(f"Cannot convert {type(value).__name__} to Short")

    def to_json(self) -> Dict[str, Any]:
        return {
            "type": "Short",
            "value": self._value
        }

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> 'Short':
        return cls(data.get("value"))

    @classmethod
    def type_name(cls) -> str:
        return "Short"


class Decimal(PalantirType[PyDecimal]):
    """高精度十进制类型"""

    def _validate(self, value: Any) -> PyDecimal:
        if isinstance(value, PyDecimal):
            return value
        elif isinstance(value, (int, float)):
            return PyDecimal(str(value))
        elif isinstance(value, str):
            try:
                return PyDecimal(value)
            except Exception:
                raise ValidationError(f"Cannot convert string '{value}' to Decimal")
        else:
            raise ValidationError(f"Cannot convert {type(value).__name__} to Decimal")

    def to_json(self) -> Dict[str, Any]:
        return {
            "type": "Decimal",
            "value": str(self._value) if self._value is not None else None
        }

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> 'Decimal':
        value = data.get("value")
        if value is not None:
            return cls(value)
        return cls()

    @classmethod
    def type_name(cls) -> str:
        return "Decimal"
