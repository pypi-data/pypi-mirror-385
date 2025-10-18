from .qzss_dcr_definition import QzssDcrDefinition

qzss_dcr_jma_seismic_intensity_upper_limit = QzssDcrDefinition(
    {
        1: "震度0",
        2: "震度1",
        3: "震度2",
        4: "震度3",
        5: "震度4",
        6: "震度5弱",
        7: "震度5強",
        8: "震度6弱",
        9: "震度6強",
        10: "震度7",
        11: "〜程度以上",
        14: "なし",
        15: "不明",
    },
    undefined="震度(上限)(コード番号：%d)"
)
