import os
import json
from lxml import etree
from tqdm import tqdm

# Define file mappings explicitly
MEETINGS = ["ES2016a", "ES2016b", "ES2016c", "ES2016d"]
BASE_PATH = r"C:\Users\babus\OneDrive\Documents\uni uzh\FS25\conversational speech processing\mypaper\Beyond-WER-in-ASR\data\amicorpus\ami_annotations\merged"
SEGMENT_PATHS = {
    "ES2016a": r"C:\Users\babus\OneDrive\Documents\uni uzh\FS25\conversational speech processing\mypaper\Beyond-WER-in-ASR\data\amicorpus\ami_annotations\merged\segments_merged\ES2016a.segments.xml",
    "ES2016b": r"C:\Users\babus\OneDrive\Documents\uni uzh\FS25\conversational speech processing\mypaper\Beyond-WER-in-ASR\data\amicorpus\ami_annotations\merged\segments_merged\ES2016b.segments.xml",
    "ES2016c": r"C:\Users\babus\OneDrive\Documents\uni uzh\FS25\conversational speech processing\mypaper\Beyond-WER-in-ASR\data\amicorpus\ami_annotations\merged\segments_merged\ES2016c.segments.xml",
    "ES2016d": r"C:\Users\babus\OneDrive\Documents\uni uzh\FS25\conversational speech processing\mypaper\Beyond-WER-in-ASR\data\amicorpus\ami_annotations\merged\segments_merged\ES2016d.segments.xml",
}
WORDS_PATHS = {
    "ES2016a": r"C:\Users\babus\OneDrive\Documents\uni uzh\FS25\conversational speech processing\mypaper\Beyond-WER-in-ASR\data\amicorpus\ami_annotations\merged\words_merged\ES2016a.words.xml",
    "ES2016b": r"C:\Users\babus\OneDrive\Documents\uni uzh\FS25\conversational speech processing\mypaper\Beyond-WER-in-ASR\data\amicorpus\ami_annotations\merged\words_merged\ES2016b.words.xml",
    "ES2016c": r"C:\Users\babus\OneDrive\Documents\uni uzh\FS25\conversational speech processing\mypaper\Beyond-WER-in-ASR\data\amicorpus\ami_annotations\merged\words_merged\ES2016c.words.xml",
    "ES2016d": r"C:\Users\babus\OneDrive\Documents\uni uzh\FS25\conversational speech processing\mypaper\Beyond-WER-in-ASR\data\amicorpus\ami_annotations\merged\words_merged\ES2016d.words.xml",
}

OUTPUT_DIR = r"C:\Users\babus\OneDrive\Documents\uni uzh\FS25\conversational speech processing\mypaper\Beyond-WER-in-ASR\data\amicorpus\ami_annotations\merged\gold\gold_references.jsonl"
def parse_segments(path):
    tree = etree.parse(path)
    root = tree.getroot()
    segments = []
    for seg in root.xpath("//segment"):
        seg_id = seg.attrib["{http://nite.sourceforge.net/}id"]
        start = float(seg.attrib["transcriber_start"])
        end = float(seg.attrib["transcriber_end"])
        segments.append({"id": seg_id, "start": start, "end": end})
    return segments

def parse_words(path):
    tree = etree.parse(path)
    root = tree.getroot()
    words = []
    for w in root.xpath("//w"):
        word = w.text
        if word is None or word.strip() == "":
            continue
        start = float(w.attrib["starttime"])
        end = float(w.attrib["endtime"])
        words.append({"word": word.strip(), "start": start, "end": end})
    return words

def align_words_to_segments(segments, words):
    transcripts = []
    for seg in segments:
        seg_start = seg["start"]
        seg_end = seg["end"]
        seg_id = seg["id"]
        seg_words = [
            w["word"]
            for w in words
            if seg_start <= w["start"] < seg_end
        ]
        reference = " ".join(seg_words)
        transcripts.append({
            "segment_id": seg_id,
            "start_time": seg_start,
            "end_time": seg_end,
            "reference": reference
        })
    return transcripts

# Write output
for meeting_id in tqdm(MEETINGS):
    segments = parse_segments(SEGMENT_PATHS[meeting_id])
    words = parse_words(WORDS_PATHS[meeting_id])
    aligned = align_words_to_segments(segments, words)

    output_path = os.path.join(OUTPUT_DIR, f"gold_references_{meeting_id}.jsonl")
    with open(output_path, "w", encoding="utf-8") as outfile:
        for entry in aligned:
            entry["meeting_id"] = meeting_id
            json.dump(entry, outfile)
            outfile.write("\n")

print(f"\n✅ Done! Gold references saved to: {OUTPUT_DIR}\\gold_references_<meeting_id>.jsonl")
