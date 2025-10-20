import pyranges as pr
from tests.helpers import assert_df_equal

a = """Chromosome Start End Strand
chr1    6    12  +
chr1    10    20 +
chr1    22    27 -
chr1    24    30 -"""
b = """Chromosome Start End Strand
chr1    12    32 +
chr1    14    30 +"""
c = """Chromosome Start End Strand
chr1    8    15 +
chr1    713800    714800 -
chr1    32    34 -"""

grs = {n: pr.from_string(s) for n, s in zip(["a", "b", "c"], [a, b, c], strict=False)}
unstranded_grs = {n: gr.remove_strand() for n, gr in grs.items()}

features = pr.PyRanges(
    {"Chromosome": ["chr1"] * 4, "Start": [0, 10, 20, 30], "End": [10, 20, 30, 40], "Strand": ["+", "+", "+", "-"]},
)
unstranded_features = features.remove_strand()


def test_strand_vs_strand_same() -> None:
    expected_result = pr.from_string(
        """Chromosome Start End Strand a b c
chr1  0 10  + 1 0 1
chr1 10 20  + 2 2 1
chr1 20 30  + 0 2 0
chr1 30 40  - 0 0 1""",
    )
    res = pr.count_overlaps(grs, features, strand_behavior="same")

    assert_df_equal(res, expected_result)


# def test_strand_vs_strand_opposite():

#     expected_result = pr.from_string("""Chromosome Start End Strand a b c
# chr1  0 10  + 1 0 1
# chr1 10 20  + 1 2 1
# chr1 20 30  + 0 2 0
# chr1 30 40  - 0 0 1""")

#     res = pr.count_overlaps(grs, features, strandedness="opposite")

#     print("features")
#     print(features)

#     for name, gr in grs.items():
#         print(name)
#         print(gr)

#     res.print(merge_position=True)

#     assert_df_equal(res.df, expected_result.df)
