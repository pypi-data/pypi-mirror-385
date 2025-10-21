## Installation

```
pip install bigwig-io
```

Requires numpy and pybind11.

## Usage

### Read bigWig and bigBed header

```python
reader = bigwig_io.open(path)
print(reader.main_header, reader.zoom_headers, reader.auto_sql, reader.total_summary)
print(reader.chr_sizes)
print(reader.type)
```

Content:
- `main_header` General file formatting info.
- `zoom_headers` Zooms levels info (reduction level and location).
- `auto_sql` BED entries declaration (only in bigBed).
- `total_summary` Statistical summary of entire file values (coverage, sums and extremes).
- `chr_sizes` Chromosomes IDs and sizes.
- `type` Either "bigwig" or "bigbed".

### Read signal

```python
values = reader.read_signal(chr_ids, starts, ends)
values = reader.read_signal(chr_ids, starts=starts, span=span)
values = reader.read_signal(chr_ids, ends=ends, span=span)
values = reader.read_signal(chr_ids, centers=centers, span=span)
```

Parameters:
- `chr_ids` `starts` `ends` `centers` Chromosomes ids, starts, ends and centers of locations. Both `starts` `ends` or one of `starts` `ends` `centers` (with `span`) may be specified.
- `span` Reading window in bp relative to locations `starts` `ends` `centers`. Only one reference may be specified if specified. Not by default.
- `bin_size` Reading bin size in bp. May varies in output if locations have variable spans or `bin_count` is specified. 1 by default.
- `bin_count` Output bin count. Inferred as max location span / bin size by default.
- `bin_mode` Method to aggregate bin values. Either "mean", "sum" or "count". "mean" by default.
- `full_bin` Extend locations ends to overlapping bins if true. Not by default.
- `def_value` Default value to use when no data overlap a bin. 0 by default.
- `zoom` BigWig zoom level to use. Use full data if -1. Auto-detect the best level if 0 by selecting the larger level whose bin size is lower that the third of `bin_size` (may be the full data). Full data by default.
- `progress` Function called during data extraction. Takes the extracted coverage and the total coverage in bp as parameters. Use default callback function if true. None by default.

Returns a numpy float32 array of shape (locations, bin count).

### Quantify signal

```python
values = reader.quantify(chr_ids, starts, ends)
```

Parameters:
- `chr_ids` `starts` `ends` `centers` `span` `bin_size` `full_bin` `def_value` `zoom` `progress` Identical to `read_signal` method.
- `reduce` Method to aggregate values over span. Either "mean", "sd", "sem", "sum", "count", "min" or "max". "mean" by default.

Returns a numpy float32 array of shape (locations).

### Profile signal

```python
values = reader.profile(chr_ids, starts, ends)
```

Parameters:
- `chr_ids` `starts` `ends` `centers` `span` `bin_size` `bin_count` `bin_mode` `full_bin` `def_value` `zoom` `progress` Identical to `read_signal` method.
- `reduce` Method to aggregate values over locations. Either "mean", "sd", "sem", "sum", "count", "min" or "max". "mean" by default.

Returns a numpy float32 array of shape (bin count).

### Read bigBed entries

```python
values = reader.read_entries(chr_ids, starts, ends)
```

Parameters:
- `chr_ids` `starts` `ends` `centers` `spans` `progress` Identical to `read_signal` method.

Returns a list (locations) of list of entries (dict with at least "chr", "start" and "end" keys).

### Convert bigWig to bedGraph or WIG

```python
reader.to_bedgraph(output_path)
reader.to_wig(output_path)
```

Parameters:
- `output_path` Path to output file.
- `chr_ids` Only extract data from these chromomes. All by default.
- `zoom` Zoom level to use. Full data by default.
- `progress` Function called during data extraction. Takes the extracted coverage and the total coverage in bp as parameters. None by default.

### Convert bigBed to BED

```python
reader.to_bed(output_path)
```

Parameters:
- `output_path` `chr_ids` `progress` Identical to `to_bedgraph` and `to_wig` methods.
- `col_count` Only write this number of columns (eg, 3 for chr, start and end). All by default.

### Write bigWig file

```python
writer = bigwig_io.open(path, "w")
writer = bigwig_io.open(path, "w", def_value=0)
writer = bigwig_io.open(path, "w", chr_sizes={"chr1": 1234, "chr2": 1234})
writer.add_entry("chr1", start=1000, end=1010, value=0.1)
writer.add_value("chr1", start=1000, span=10, value=0.1)
writer.add_values("chr1", start=1000, span=10, values=[0.1, 0.1, 0.1, 0.1])
```
must be pooled by chr, and sorted by (1) start (2) end
no overlap


### Write bigBed file

```python
writer = bigwig_io.open(path, "w", type="bigbed")
writer = bigwig_io.open(path, "w", type="bigbed", chr_sizes={"chr1": 1234, "chr2": 1234})
writer = bigwig_io.open(path, "w", type="bigbed", fields=["chr", "start", "end", "name"])
writer = bigwig_io.open(path, "w", type="bigbed", fields={"chr": "string", "start", "uint", "end": "uint", "name": "string"})
writer.add_entry("chr1", start=1000, end=1010)
writer.add_entry("chr1", start=1000, end=1010, fields={"name": "read#1"})
```
must be pooled by chr, and sorted by (1) start (2) end
may be overlapping



