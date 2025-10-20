use std::{
    fmt::Debug,
    fs::File,
    io::{BufRead, BufReader, BufWriter, Write},
    path::Path,
    str::FromStr,
};

use coitrees::Interval;
use eyre::Context;
use itertools::Itertools;
use noodles::{
    bgzf::{self, IndexedReader},
    fasta,
};
use polars::prelude::*;

use crate::{config::Config, preset::Preset};

/// Write TSV file to file or stdout.
pub fn write_tsv(df: &mut DataFrame, path: Option<impl AsRef<Path>>) -> eyre::Result<()> {
    let mut file: Box<dyn Write> = if let Some(path) = path {
        Box::new(BufWriter::new(File::create(path)?))
    } else {
        Box::new(BufWriter::new(std::io::stdout()))
    };
    CsvWriter::new(&mut file)
        .include_header(true)
        .with_separator(b'\t')
        .finish(df)?;
    Ok(())
}

#[allow(unused)]
pub fn write_itvs<T: Debug + Clone>(
    itvs: impl Iterator<Item = Interval<T>>,
    path: Option<impl AsRef<Path>>,
) -> eyre::Result<()> {
    let mut file: Box<dyn Write> = if let Some(path) = path {
        Box::new(BufWriter::new(File::create(path)?))
    } else {
        Box::new(BufWriter::new(std::io::stdout()))
    };
    for itv in itvs {
        writeln!(&mut file, "{}\t{}\t{:?}", itv.first, itv.last, itv.metadata)?;
    }
    Ok(())
}

/// Read a BED file and return a list of [`Interval`]s.
///
/// # Arguments
/// * `bed`: Bedfile path.
/// * `intervals_fn`: Function applied to `(start, stop, other_cols)` to convert into an [`Interval`].
///
/// # Examples
/// BED3 record.
/// ```
/// use rs_nucflag::io::read_bed;
/// use coitrees::Interval;
///
/// let records = read_bed(
///     "core/test/standard/region.bed",
///     |name: &str, start: u64, stop: u64, other_cols: &str| Interval::new(start as i32, stop as i32, None::<&str>)
/// );
/// ```
/// BED4 record
/// ```
/// use rs_nucflag::io::read_bed;
/// use coitrees::Interval;
///
/// let records = read_bed(
///     "core/test/standard/region.bed",
///     |name: &str, start: u64, stop: u64, other_cols: &str| Interval::new(start as i32, stop as i32, Some(other_cols.to_owned()))
/// );
/// ```
pub fn read_bed<T: Clone + Debug>(
    bed: impl AsRef<Path>,
    intervals_fn: impl Fn(&str, u64, u64, &str) -> Interval<T>,
) -> Option<Vec<Interval<T>>> {
    let mut intervals = Vec::new();
    let bed_fh = File::open(bed).ok()?;
    let bed_reader = BufReader::new(bed_fh);

    for line in bed_reader.lines() {
        let Ok(line) = line else {
            log::error!("Invalid line: {line:?}");
            continue;
        };
        let (name, start, stop, other_cols) =
            if let Some((name, start, stop, other_cols)) = line.splitn(4, '\t').collect_tuple() {
                (name, start, stop, other_cols)
            } else if let Some((name, start, stop)) = line.splitn(3, '\t').collect_tuple() {
                (name, start, stop, "")
            } else {
                log::error!("Invalid line: {line}");
                continue;
            };
        let (Ok(first), Ok(last)) = (start.parse::<u64>(), stop.parse::<u64>()) else {
            log::error!("Cannot parse {start} or {stop} for {line}");
            continue;
        };

        intervals.push(intervals_fn(name, first, last, other_cols))
    }
    Some(intervals)
}

pub fn read_cfg(path: Option<impl AsRef<Path>>, preset: Option<&str>) -> eyre::Result<Config> {
    match (path, preset.map(Preset::from_str)) {
        (None, None) => Ok(Config::default()),
        (None, Some(preset)) => {
            let preset = preset?;
            Ok(Config::from(preset))
        }
        (Some(cfg_path), None) => {
            let cfg_str = std::fs::read_to_string(cfg_path)?;
            toml::from_str(&cfg_str).map_err(Into::into)
        }
        (Some(cfg_path), Some(preset)) => {
            let preset = preset?;
            let cfg_str = std::fs::read_to_string(cfg_path)?;
            let cfg: Config = toml::from_str(&cfg_str)?;
            let preset_cfg = Config::from(preset);
            Ok(cfg.merge(preset_cfg))
        }
    }
}

pub enum FastaReader {
    Bgzip(fasta::io::Reader<IndexedReader<File>>),
    Standard(fasta::io::Reader<BufReader<File>>),
}

pub struct FastaHandle {
    pub reader: FastaReader,
    pub fai: fasta::fai::Index,
}

impl FastaHandle {
    pub fn new(infile: impl AsRef<Path>) -> eyre::Result<Self> {
        let (fai, gzi) = Self::get_faidx(&infile)?;
        let fh = Self::read_fa(&infile, gzi.as_ref())?;
        Ok(Self { reader: fh, fai })
    }

    fn get_faidx(
        fa: &impl AsRef<Path>,
    ) -> eyre::Result<(fasta::fai::Index, Option<bgzf::gzi::Index>)> {
        // https://www.ginkgobioworks.com/2023/03/17/even-more-rapid-retrieval-from-very-large-files-with-rust/
        let fa_path = fa.as_ref().canonicalize()?;
        let is_bgzipped = fa_path.extension().and_then(|e| e.to_str()) == Some("gz");
        let mut fai_fname = fa_path.clone();
        fai_fname.as_mut_os_string().push(".fai");

        let fai = fasta::fai::read(fai_fname);
        if is_bgzipped {
            let index_reader = bgzf::io::indexed_reader::Builder::default()
                .build_from_path(fa)
                .with_context(|| format!("Failed to read gzi for {fa_path:?}"))?;
            let gzi = index_reader.index().clone();

            if let Ok(fai) = fai {
                log::debug!("Existing fai index found for {fa_path:?}");
                return Ok((fai, Some(gzi)));
            }
            log::debug!("No existing faidx for {fa_path:?}. Generating...");
            let mut records = Vec::new();
            let mut indexer = fasta::io::Indexer::new(index_reader);
            while let Some(record) = indexer.index_record()? {
                records.push(record);
            }

            Ok((fasta::fai::Index::from(records), Some(gzi)))
        } else {
            if let Ok(fai) = fai {
                return Ok((fai, None));
            }
            log::debug!("No existing faidx for {fa_path:?}. Generating...");
            Ok((fasta::index(fa)?, None))
        }
    }

    pub fn fetch(&mut self, ctg_name: &str, start: u32, stop: u32) -> eyre::Result<fasta::Record> {
        let start_pos = noodles::core::Position::new(start.clamp(1, u32::MAX) as usize).unwrap();
        let stop_pos = noodles::core::Position::new(stop.clamp(1, u32::MAX) as usize).unwrap();
        let region = noodles::core::Region::new(ctg_name, start_pos..=stop_pos);
        match &mut self.reader {
            FastaReader::Bgzip(reader) => Ok(reader.query(&self.fai, &region)?),
            FastaReader::Standard(reader) => Ok(reader.query(&self.fai, &region)?),
        }
    }

    fn read_fa(
        fa: &impl AsRef<Path>,
        fa_gzi: Option<&bgzf::gzi::Index>,
    ) -> eyre::Result<FastaReader> {
        let fa_file = std::fs::File::open(fa);
        if let Some(fa_gzi) = fa_gzi {
            Ok(FastaReader::Bgzip(
                fa_file
                    .map(|file| bgzf::IndexedReader::new(file, fa_gzi.clone()))
                    .map(fasta::io::Reader::new)?,
            ))
        } else {
            Ok(FastaReader::Standard(
                fa_file
                    .map(std::io::BufReader::new)
                    .map(fasta::io::Reader::new)?,
            ))
        }
    }
}
