from .qzss_dcr_definition import QzssDcrDefinition

qzss_dcr_jma_marine_warning_code = QzssDcrDefinition(
    {
        0: "海上警報解除",
        10: "海上着氷警報",
        11: "海上濃霧警報",
        12: "海上うねり警報",
        20: "海上風警報",
        21: "海上強風警報",
        22: "海上暴風警報",
        23: "海上台風警報",
        31: "その他の警報等情報要素 海上警報",
        # 'NN*': "警報等情報要素_海上警報(コード番号：NN)",
    },
    undefined="警報等情報要素_海上警報(コード番号：%d)"
)
