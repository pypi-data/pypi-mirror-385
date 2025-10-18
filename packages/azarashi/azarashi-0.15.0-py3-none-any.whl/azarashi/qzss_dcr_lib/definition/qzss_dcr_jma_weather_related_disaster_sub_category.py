from .qzss_dcr_definition import QzssDcrDefinition

qzss_dcr_jma_weather_related_disaster_sub_category = QzssDcrDefinition(
    {
        1: "暴風雪特別警報",
        2: "大雨特別警報",
        3: "暴風特別警報",
        4: "大雪特別警報",
        5: "波浪特別警報",
        6: "高潮特別警報",
        7: "全ての気象特別警報",
        21: "記録的短時間大雨情報",
        22: "竜巻注意情報",
        23: "土砂災害警戒情報",
        31: "その他の警報等情報要素",
        # "NN*": "警報等情報要素(コード番号：NN)",
    },
    undefined="警報等情報要素(コード番号：%d)"
)
