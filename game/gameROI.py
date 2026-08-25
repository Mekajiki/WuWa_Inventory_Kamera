class Coordinates:
    def __init__(self, x: int | float = 0, y: int | float = 0, w: int | float = 0, h: int | float = 0):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    def __repr__(self):
        return f"Coordinates(x={self.x}, y={self.y}, w={self.w}, h={self.h})"

    def __reduce__(self):
        return (self.__class__, (self.x, self.y, self.w, self.h))

COORDINATES = {
    (16, 9): {
        (1920, 1080): {
            "terminal": Coordinates(140, 40, 150, 40),
            "shell": Coordinates(1255, 38, 165, 50),
            "offsets": {
                "page": Coordinates(16, 24)
            },
            "scroll": {
                "page": Coordinates(y=-31.25),
                "characters": Coordinates(y=-56),
                "sonata": Coordinates(y=70)
            },
            "scrapers": {
                "weapons": Coordinates(81.5, 191.5),
                "echoes": Coordinates(81.5, 326.5),
                "devItems": Coordinates(81.5, 596.5),
                "resources": Coordinates(81.5, 731.5),
            },
            "items": {
                "start": Coordinates(205, 122, 151, 181),
                "info": Coordinates(1296, 114, 558, 278),
                "description": Coordinates(1296, 114, 558, 820)
            },
            "weapons": {
                "page": Coordinates(200, 50, 130, 40),
                "start": Coordinates(205, 122, 151, 181),
                "name": Coordinates(1305, 116, 545, 55),
                "value": Coordinates(1655, 320, 190, 40),
                "level": Coordinates(1660, 235, 180, 45),
                "rank": Coordinates(1300, 530, 115, 50)
            },
            "echoes": {
                "page": Coordinates(200, 50, 130, 40),
                "start": Coordinates(205, 122, 151, 181),
                "echoCard": Coordinates(1296, 114, 558, 170),
                "sonata": Coordinates(1298, 397, 554, 467),
                "mouseMovement": Coordinates(1576.5, 665.5),
                "fullStatsName": Coordinates(1380, 430, 360, 380),
                "fullStatsValue": Coordinates(1740, 430, 100, 380)
            },
            "achievements": {
                "status": Coordinates(1579, 230, 256, 65),
                "searchBar": Coordinates(388, 149),
                "searchButton": Coordinates(629, 149),
                "achievementsButton": Coordinates(1674, 790),
                "achievementsTab": Coordinates(835, 570),
            },
            "characters": {
                # Layout measured against the 3.6 client (2026-08). The skill
                # screen now shows levels directly on the tree, so skills and
                # chains are read from screenshots without clicking nodes.
                "offsets": {
                    "leftSide": Coordinates(y=136),
                    "rightSide": Coordinates(y=134)
                },
                "leftSide": Coordinates(82, 191),
                "rightSide": Coordinates(1819, 221),
                "resonatorName": Coordinates(200, 200, 300, 40),
                "resonatorLevel": Coordinates(200, 254, 150, 36),
                "weaponName": Coordinates(205, 204, 330, 38),
                "weaponLevel": Coordinates(200, 266, 150, 34),
                "weaponRank": Coordinates(210, 428, 120, 32),
                # One horizontal band containing all five "Lv.X/10" labels;
                # each label is assigned to the nearest column center.
                "skillStrip": Coordinates(300, 750, 1320, 280),
                "skillColumns": [
                    Coordinates(x=466),
                    Coordinates(x=691),
                    Coordinates(x=963),
                    Coordinates(x=1230),
                    Coordinates(x=1453)
                ],
                "chainPositions": [
                    Coordinates(1545, 282),
                    Coordinates(1519, 508),
                    Coordinates(1438, 680),
                    Coordinates(1309, 824),
                    Coordinates(1146, 924),
                    Coordinates(943, 963)
                ]
            }
        }
    },
    (16, 10): {
        (1680, 1050): {
            "terminal": Coordinates(125, 32, 150, 40),
            "shell": Coordinates(1100, 35, 145, 40),
            "offsets": {
                "page": Coordinates(16, 24),
                "characters": Coordinates(y=-56),
                "sonata": Coordinates(y=70),
            },
            "scroll": {
                "page": Coordinates(y=-31.70),
                "characters": Coordinates(y=-56),
                "sonata": Coordinates(y=70)
            },
            "scrapers": {
                "weapons": Coordinates(71.5, 167),
                "echoes": Coordinates(71.5, 285),
                "devItems": Coordinates(71.5, 521),
                "resources": Coordinates(71.5, 639),
            },
            "items": {
                "start": Coordinates(180, 104, 130, 162),
                "info": Coordinates(1136, 154, 485, 240),
                "description": Coordinates(1136, 154, 485, 715)
            },
            "weapons": {
                "page": Coordinates(175, 40, 130, 40),
                "start": Coordinates(180, 104, 130, 162),
                "name": Coordinates(1140, 152, 480, 50),
                "value": Coordinates(1430, 330, 190, 40),
                "level": Coordinates(1435, 255, 180, 45),
                "rank": Coordinates(1135, 510, 100, 50)
            },
            "echoes": {
                "page": Coordinates(175, 40, 130, 40),
                "start": Coordinates(180, 104, 130, 162),
                "echoCard": Coordinates(1136, 152, 486, 152),
                "sonata": Coordinates(1135, 400, 486, 408),
                "mouseMovement": Coordinates(1576.5, 665.5),
                "fullStatsName": Coordinates(1200, 420, 320, 380),
                "fullStatsValue": Coordinates(1510, 420, 100, 380)
            },
            "achievements": {
                "status": Coordinates(1579, 197, 256, 65),
                "searchBar": Coordinates(388, 129),
                "searchButton": Coordinates(550, 129),
                "achievementsButton": Coordinates(1465, 690),
                "achievementsTab": Coordinates(735, 570),
            },
            "characters": {
                # Rough 16:10 projection of the 3.6 16:9 layout (untested).
                "offsets": {
                    "leftSide": Coordinates(y=119),
                    "rightSide": Coordinates(y=130)
                },
                "leftSide": Coordinates(68, 167.5),
                "rightSide": Coordinates(1592, 215),
                "resonatorName": Coordinates(175, 194, 263, 39),
                "resonatorLevel": Coordinates(175, 247, 131, 35),
                "weaponName": Coordinates(179, 198, 289, 37),
                "weaponLevel": Coordinates(175, 259, 131, 33),
                "weaponRank": Coordinates(184, 416, 105, 31),
                "skillStrip": Coordinates(263, 729, 1155, 272),
                "skillColumns": [
                    Coordinates(x=408),
                    Coordinates(x=605),
                    Coordinates(x=843),
                    Coordinates(x=1076),
                    Coordinates(x=1271)
                ],
                "chainPositions": [
                    Coordinates(1352, 274),
                    Coordinates(1329, 494),
                    Coordinates(1258, 661),
                    Coordinates(1145, 801),
                    Coordinates(1003, 898),
                    Coordinates(825, 936)
                ]
            }
        }
    }
}