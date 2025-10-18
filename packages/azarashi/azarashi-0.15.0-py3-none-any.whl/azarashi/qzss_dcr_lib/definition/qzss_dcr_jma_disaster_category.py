from .qzss_dcr_definition import QzssDcrDefinition

qzss_dcr_jma_disaster_category = QzssDcrDefinition(
    {
        1: '緊急地震速報',
        2: '震源',
        3: '震度',
        4: '南海トラフ地震',
        5: '津波',
        6: '北西太平洋津波',
        # 7 : '未使用',
        8: '火山',
        9: '降灰',
        10: '気象',
        11: '洪水',
        12: '台風',
        # 13: '未使用',
        14: '海上',
    },
    undefined=None
)

qzss_dcr_jma_disaster_category_en = QzssDcrDefinition(
    {
        1: 'Earthquake Early Warning',
        2: 'Hypocenter',
        3: 'Seismic Intensity',
        4: 'Nankai Trough Earthquake',
        5: 'Tsunami',
        6: 'Northwest Pacific Tsunami',
        # 7 : 'Unused',
        8: 'Volcano',
        9: 'Ash Fall',
        10: 'Weather',
        11: 'Flood',
        12: 'Typhoon',
        # 13: 'Unused',
        14: 'Marine',
    },
    undefined=None
)
