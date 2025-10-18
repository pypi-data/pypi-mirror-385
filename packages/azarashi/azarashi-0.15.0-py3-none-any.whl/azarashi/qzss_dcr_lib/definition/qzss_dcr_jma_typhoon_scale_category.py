from .qzss_dcr_definition import QzssDcrDefinition

qzss_dcr_jma_typhoon_scale_category = QzssDcrDefinition(
    {
        0: "なし",
        1: "大型",
        2: "超大型",
        15: "その他の大きさ階級分類",
        # "NN*": "大きさ階級分類(コード番号：NN)",
    },
    undefined="大きさ階級分類(コード番号：%d)"
)
