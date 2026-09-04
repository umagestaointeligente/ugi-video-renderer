from __future__ import annotations
import hashlib, json
from pathlib import Path

HERE=Path(__file__).resolve().parent
ENGINE_FILES=(
    'common.py','prepare.py','render.py','qa.py','voice.py','fingerprint.py','contract_v9_factory.json'
)


def _digest(payload):
    return hashlib.sha256(
        json.dumps(payload,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()
    ).hexdigest()


def _file_digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def engine_fingerprint():
    rows=[]
    for name in ENGINE_FILES:
        p=HERE/name
        if not p.exists():
            raise RuntimeError(f'ENGINE_FINGERPRINT_FILE_MISSING {name}')
        rows.append({'path':name,'sha256':_file_digest(p)})
    return _digest(rows)


def prepared_asset_fingerprint(item):
    """Only item fields that can change prepared media bytes or timing."""
    keys=(
        'id','caption_chunks','scene_plan','music_profile','music_track',
        'source_url','source_sha256'
    )
    return _digest({k:item.get(k) for k in keys})


def prepared_contract_fingerprint(c):
    music=c.get('music',{})
    payload={
        'voice':c.get('voice'),
        'story':c.get('story'),
        'cta':{
            'spoken_line':c.get('cta',{}).get('spoken_line'),
            'duration_seconds':c.get('cta',{}).get('duration_seconds')
        },
        'canvas':{
            'fps':c.get('canvas',{}).get('fps'),
            'sample_rate':c.get('canvas',{}).get('sample_rate')
        },
        'prepared_music':{
            'master_lufs':music.get('prepared_master_lufs'),
            'master_true_peak_dbtp':music.get('prepared_master_true_peak_dbtp')
        }
    }
    return _digest(payload)


def dispatch_fingerprint(item):
    """Media/gate identity. Mutable schedule/readback freshness is validated live separately."""
    keys=(
        'id','work_type','film_title','film_year','rights_evidence','license',
        'anti_repeat_evidence','caption_chunks','scene_plan','music_track',
        'source_url','source_sha256'
    )
    return _digest({k:item.get(k) for k in keys})


def schedule_fingerprint(item):
    return _digest({'id':item.get('id'),'schedule':item.get('schedule')})


def item_fingerprint(item):
    return prepared_asset_fingerprint(item)
