import json

def cetak_alasan(fakta, alasan, indent=2):
    if fakta in alasan:
        r = alasan[fakta]
        spasi = " " * indent
        syarat_aktif = [s for s in r["jika"] if s in r["memori_saat_itu"]]
        print(f"{spasi}{fakta} <- {r['id']} ({', '.join(syarat_aktif)}) [Sumber: {r['sumber']}]")
        for s in syarat_aktif:
            cetak_alasan(s, alasan, indent + 2)

def main():
    with open("kb_pompa.json", "r", encoding="utf-8") as f:
        kb = json.load(f)

    print(kb["judul"])
    print("Jawab y/t.")

    # Pisahkan fakta dasar (ditanyakan ke user) dan kesimpulan akhir (tidak pernah jadi syarat aturan lain)
    semua_syarat = {s for r in kb["aturan"] for s in r["jika"]}
    semua_maka = {r["maka"] for r in kb["aturan"]}
    
    fakta_dasar = [s for r in kb["aturan"] for s in r["jika"] if s not in semua_maka]
    fakta_dasar = list(dict.fromkeys(fakta_dasar)) # Hapus duplikat dengan menjaga urutan
    kesimpulan_akhir = semua_maka - semua_syarat

    # 1. Tanya fakta dasar ke user
    memori = []
    for i, fakta in enumerate(fakta_dasar, 1):
        jawab = input(f"{i}. Apakah {fakta}? (y/t) > ").strip().lower()
        if jawab == "y":
            memori.append(fakta)

    print(f"\nFakta awal: {', '.join(memori) if memori else 'tidak ada'}\n")

    # 2. Mesin Inferensi Forward Chaining (sesuai pseudocode soal: ambil cocok[0] tiap siklus)
    alasan = {}
    siklus = 1
    while True:
        cocok = []
        for r in kb["aturan"]:
            if r["maka"] in memori:
                continue
            if r["mode"] == "dan" and all(s in memori for s in r["jika"]):
                cocok.append(r)
            elif r["mode"] == "atau" and any(s in memori for s in r["jika"]):
                cocok.append(r)

        if not cocok:
            print(f"Siklus {siklus}: tidak ada aturan baru, berhenti")
            break

        r = cocok[0]
        memori.append(r["maka"])
        alasan[r["maka"]] = {
            "id": r["id"],
            "jika": r["jika"],
            "sumber": r["sumber"],
            "memori_saat_itu": list(memori)
        }
        print(f"Siklus {siklus}: {r['id']} -> {r['maka']}")
        siklus += 1

    # 3. Tampilkan Kesimpulan Akhir & Alasan
    hasil = [f for f in memori if f in kesimpulan_akhir]
    
    if not hasil:
        print("\nKesimpulan: tidak ada (kasus negatif)")
    else:
        print(f"\nKesimpulan: {', '.join(hasil)}")
        print("Alasan:")
        for h in hasil:
            cetak_alasan(h, alasan)

    print(f"\nCatatan: {kb['batas']}")

if __name__ == "__main__":
    main()