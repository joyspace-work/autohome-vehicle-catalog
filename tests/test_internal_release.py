import json

from autohome_catalog.internal_release import IMAGE_FIELD, gallery_status, visible_plan


def test_status_does_not_claim_cover_is_gallery():
    row = {IMAGE_FIELD: '["https://example.org/a.jpg"]', "图片数": 1,
           "图库分组JSON": json.dumps([{"图片类别": "车系封面", "图片URL": ["a"]}])}
    assert gallery_status(row)[0] == "部分"
    row["图片数"] = 2
    assert gallery_status(row)[0] == "待核验"
    row[IMAGE_FIELD] = "invalid"
    assert gallery_status(row)[0] == "待核验"


def test_access_limit_and_empty_are_separate():
    row = {IMAGE_FIELD: "[]", "图片数": 0, "图片说明": "HTTP429"}
    assert gallery_status(row)[0] == "来源暂停"
    row["图片说明"] = ""
    assert gallery_status(row)[0] == "待采"


def test_parameter_order_and_business_links_are_preserved():
    names = ["车型全称", "来源车系ID", "能源类型", "长*宽*高(mm)", "对应配置", "来源配置ID"]
    assert visible_plan("基本参数", [{"name": n} for n in names], names) == [
        "车型全称", "能源类型", "长*宽*高(mm)", "对应配置"]
