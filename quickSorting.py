
text = "Brewer's supplies 20 gp 9 lb.\n" \
    "Calligrapher's supplies 10 gp 5 lb.\n" \
    "Carpenter's tools 8 gp 6 lb.\n" \
    "Cartographer's tools 15 gp 6 lb.\n" \
    "Cobbler's tools 5 gp 5 lb.\n" \
    "Cook's utensils 1 gp 8 lb.\n" \
    "Jeweler's tools 25 gp 2 lb.\n" \
    "Leatherworker's tools 5 gp 5 lb.\n" \
    "Mason's tools 10 gp 8 lb.\n" \
    "Painter's supplies 10 gp 5 lb.\n" \
    "Smith's tools 20 gp 8 lb.\n" \
    "Tinker's tools 50 gp 10 lb.\n" \
    "Weaver's tools 1 gp 5 lb.\n" \
    "Woodcarver's tools 1 gp 5 lb."

text = text.split("\n")
for line in text:
    words = line.split(" ")
    name = words[0] + " " + words[1]
    price = words[2] + " " + words[3]
    weight = words[4]
    lowername = name.lower().replace("'", "").replace(" ", "_")
    print(f'{lowername}:')
    print(f'    name: "{name}"')
    print(f'    cost: "{price}"')
    print(f"    weight: {weight}")