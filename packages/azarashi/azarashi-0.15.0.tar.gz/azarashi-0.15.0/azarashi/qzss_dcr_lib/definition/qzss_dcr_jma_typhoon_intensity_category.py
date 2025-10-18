from .qzss_dcr_definition import QzssDcrDefinition

qzss_dcr_jma_typhoon_intensity_category = QzssDcrDefinition(
    {
        0: "なし",
        1: "強い",
        2: "非常に強い",
        3: "猛烈な",
        15: "その他の強さ階級分類",
        # "NN*": "強さ階級分類(コード番号：NN)",
    },
    undefined="強さ階級分類(コード番号：%d)"
)
