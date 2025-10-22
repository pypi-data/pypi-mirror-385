class Himpunan:
    def __init__(self, *args):
        # Inisialisasi himpunan menggunakan list unik (tanpa duplikat)
        self.data = []
        for item in args:
            if item not in self.data:
                self.data.append(item)

    def __repr__(self):
        # Representasi string saat diprint
        return "{" + ", ".join(map(str, self.data)) + "}"

    def __len__(self):
        # Mengembalikan jumlah elemen
        return len(self.data)

    def __contains__(self, item):
        # Mengecek apakah item ada dalam himpunan
        return item in self.data

    def __eq__(self, other):
        # Mengecek apakah dua himpunan sama
        return sorted(self.data) == sorted(other.data)

    def __le__(self, other):
        # Mengecek subset
        return all(item in other.data for item in self.data)

    def __lt__(self, other):
        # Proper subset (subset tapi tidak sama)
        return self <= other and self != other

    def __ge__(self, other):
        # Superset
        return all(item in self.data for item in other.data)

    def __floordiv__(self, other):
        # Ekuivalen (elemen sama, urutan boleh berbeda)
        return set(self.data) == set(other.data)

    def __add__(self, other):
        # Gabungan dua himpunan (union)
        result = Himpunan(*self.data)
        for item in other.data:
            if item not in result.data:
                result.data.append(item)
        return result

    def __sub__(self, other):
        # Selisih dua himpunan
        result = Himpunan(*[item for item in self.data if item not in other.data])
        return result

    def __truediv__(self, other):
        # Irisan dua himpunan
        result = Himpunan(*[item for item in self.data if item in other.data])
        return result

    def __mul__(self, other):
        # Selisih simetris (elemen yang hanya ada di salah satu)
        result = Himpunan(*[item for item in self.data if item not in other.data] +
                          [item for item in other.data if item not in self.data])
        return result

    def __pow__(self, other):
        # Produk Kartesius
        result = Himpunan(*[(a, b) for a in self.data for b in other.data])
        return result

    def __abs__(self):
        # Himpunan kuasa (power set)
        from itertools import chain, combinations
        subset_list = list(chain.from_iterable(combinations(self.data, r) for r in range(len(self.data)+1)))
        return len(subset_list)
    
    def __iadd__(self, item):
        # Operator += untuk menambah elemen tunggal
        if item not in self.data:
            self.data.append(item)
        return self

    def ListKuasa(self):
        # Menampilkan semua subset dalam bentuk list
        from itertools import chain, combinations
        subset_list = list(chain.from_iterable(combinations(self.data, r) for r in range(len(self.data)+1)))
        return [Himpunan(*s) for s in subset_list]  

    def tambah(self, item):
        # Menambah elemen baru
        if item not in self.data:
            self.data.append(item)

    def hapus(self, item):
        # Menghapus elemen dari himpunan
        if item in self.data:
            self.data.remove(item)

    def Komplement(self, semester):
        # Mengembalikan komplemen dari himpunan terhadap himpunan semester
        return Himpunan(*[item for item in semester.data if item not in self.data])
