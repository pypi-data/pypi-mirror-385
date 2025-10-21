class Himpunan:
    def __init__(self, *elemen):
        """Inisialisasi himpunan dari sekumpulan elemen unik."""
        self.data = []
        for e in elemen:
            if e not in self.data:
                self.data.append(e)

    def __repr__(self):
        """Representasi string dari himpunan."""
        return "{" + ", ".join(map(str, self.data)) + "}"

    def __len__(self):
        """Mengembalikan jumlah elemen dalam himpunan."""
        return len(self.data)

    def __contains__(self, item):
        """True jika item ada dalam himpunan."""
        return item in self.data

    def __eq__(self, other):
        """True jika dua himpunan memiliki elemen yang sama (urutan tidak diperhitungkan)."""
        if len(self) != len(other):
            return False
        return all(e in other for e in self.data)

    def __le__(self, other):
        """True jika himpunan ini subset dari himpunan lain."""
        return all(e in other for e in self.data)

    def __lt__(self, other):
        """True jika himpunan ini proper subset dari himpunan lain."""
        return self <= other and self != other

    def __ge__(self, other):
        """True jika himpunan ini superset dari himpunan lain."""
        return all(e in self.data for e in other.data)

    def __floordiv__(self, other):
        """True jika dua himpunan ekuivalen (memiliki elemen yang sama meskipun urutannya berbeda)."""
        return self == other

    # Operator / → Irisan
    def __truediv__(self, other):
        """Mengembalikan irisan dua himpunan."""
        result = [e for e in self.data if e in other.data]
        return Himpunan(*result)

    # Operator + → Gabungan
    def __add__(self, other):
        """Mengembalikan gabungan dua himpunan."""
        result = self.data.copy()
        for e in other.data:
            if e not in result:
                result.append(e)
        return Himpunan(*result)

    # Operator - → Selisih
    def __sub__(self, other):
        """Mengembalikan selisih dua himpunan (elemen di self tapi tidak di other)."""
        result = [e for e in self.data if e not in other.data]
        return Himpunan(*result)

    # Operator * → Selisih Simetris
    def __mul__(self, other):
        """Mengembalikan selisih simetris dua himpunan."""
        result = [e for e in self.data if e not in other.data] + \
                 [e for e in other.data if e not in self.data]
        return Himpunan(*result)

    # Operator ** → Cartesian Product
    def __pow__(self, other):
        """Mengembalikan hasil Cartesian Product dua himpunan sebagai tuple."""
        result = [(a, b) for a in self.data for b in other.data]
        return Himpunan(*result)

    # abs() → Power Set
    def __abs__(self):
        """Mengembalikan power set dari himpunan."""
        return Himpunan(*self.ListKuasa())

    def ListKuasa(self):
        """Menghasilkan list dari seluruh subset yang mungkin (power set)."""
        subsets = [[]]
        for e in self.data:
            subsets += [subset + [e] for subset in subsets]
        return [Himpunan(*subset) for subset in subsets]

    # Tambah anggota
    def __iadd__(self, item):
        """Menambah elemen baru ke dalam himpunan."""
        if item not in self.data:
            self.data.append(item)
        return self

    # Hapus anggota
    def remove(self, item):
        """Menghapus elemen dari himpunan."""
        if item in self.data:
            self.data.remove(item)

    # Komplemen terhadap himpunan semesta
    def Komplemen(self, semesta):
        """Mengembalikan komplemen dari himpunan terhadap himpunan semesta."""
        result = [e for e in semesta.data if e not in self.data]
        return Himpunan(*result)
