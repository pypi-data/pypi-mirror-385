"""値オブジェクトのテスト"""
from uuid import UUID, uuid4
import pytest

from inheritance_calculator_core.models.value_objects import PersonID


class TestPersonID:
    """PersonID値オブジェクトのテスト"""

    def test_generate(self) -> None:
        """新しいPersonIDを生成できる"""
        person_id = PersonID.generate()
        assert isinstance(person_id, PersonID)
        assert isinstance(person_id.value, UUID)

    def test_generate_creates_unique_ids(self) -> None:
        """generate()は毎回異なるIDを生成する"""
        id1 = PersonID.generate()
        id2 = PersonID.generate()
        assert id1 != id2

    def test_from_string(self) -> None:
        """文字列からPersonIDを生成できる"""
        uuid_str = "550e8400-e29b-41d4-a716-446655440000"
        person_id = PersonID.from_string(uuid_str)
        assert isinstance(person_id, PersonID)
        assert person_id.value == UUID(uuid_str)

    def test_from_string_invalid_raises_error(self) -> None:
        """無効な文字列からPersonIDを生成しようとするとエラー"""
        with pytest.raises(ValueError):
            PersonID.from_string("invalid-uuid")

    def test_from_uuid(self) -> None:
        """UUIDからPersonIDを生成できる"""
        uuid_val = uuid4()
        person_id = PersonID.from_uuid(uuid_val)
        assert isinstance(person_id, PersonID)
        assert person_id.value == uuid_val

    def test_str(self) -> None:
        """文字列表現を取得できる"""
        uuid_str = "550e8400-e29b-41d4-a716-446655440000"
        person_id = PersonID.from_string(uuid_str)
        assert str(person_id) == uuid_str

    def test_repr(self) -> None:
        """デバッグ用文字列表現を取得できる"""
        uuid_str = "550e8400-e29b-41d4-a716-446655440000"
        person_id = PersonID.from_string(uuid_str)
        assert repr(person_id) == f"PersonID('{uuid_str}')"

    def test_equality(self) -> None:
        """等値比較ができる"""
        uuid_str = "550e8400-e29b-41d4-a716-446655440000"
        id1 = PersonID.from_string(uuid_str)
        id2 = PersonID.from_string(uuid_str)
        id3 = PersonID.generate()

        assert id1 == id2
        assert id1 != id3
        assert id2 != id3

    def test_equality_with_non_person_id(self) -> None:
        """PersonID以外との比較でFalse"""
        person_id = PersonID.generate()
        assert person_id != "not a PersonID"
        assert person_id != 123
        assert person_id != None

    def test_hashable(self) -> None:
        """ハッシュ可能で辞書のキーとして使える"""
        id1 = PersonID.generate()
        id2 = PersonID.generate()

        # 辞書のキーとして使用
        data = {id1: "value1", id2: "value2"}
        assert data[id1] == "value1"
        assert data[id2] == "value2"

    def test_hashable_same_ids_have_same_hash(self) -> None:
        """同じUUIDを持つPersonIDは同じハッシュ値を持つ"""
        uuid_str = "550e8400-e29b-41d4-a716-446655440000"
        id1 = PersonID.from_string(uuid_str)
        id2 = PersonID.from_string(uuid_str)

        assert hash(id1) == hash(id2)

    def test_immutable(self) -> None:
        """値オブジェクトは不変"""
        person_id = PersonID.generate()

        # frozen=Trueなので属性変更は不可
        with pytest.raises(AttributeError):
            person_id.value = uuid4()  # type: ignore

    def test_can_be_used_in_set(self) -> None:
        """セットの要素として使用できる"""
        id1 = PersonID.generate()
        id2 = PersonID.generate()
        id3 = PersonID.from_string(str(id1))  # id1と同じ

        id_set = {id1, id2, id3}
        # id1とid3は同じなので、セットには2要素のみ
        assert len(id_set) == 2
        assert id1 in id_set
        assert id2 in id_set
        assert id3 in id_set
