import re


VARIANT_PATTERN = re.compile(
  r"""^\s*
    (?P<chrom>[1-9]|1[0-9]|2[0-2])
    -
    (?P<pos>[1-9]\d{0,8})
    -
    (?P<ref>[ACGT])
    -
    (?P<alt>[ACGT])
    \s*$""",
  re.IGNORECASE | re.VERBOSE
)
