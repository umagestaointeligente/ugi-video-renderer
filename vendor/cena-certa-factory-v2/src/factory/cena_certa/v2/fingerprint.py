from __future__ import annotations
import hashlib, json


def _digest(payload):
    return hashlib.sha256(
        json.dumps(payload,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()
    ).hexdigest()


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
    """Fingerprint of the live item state used for the timed dispatch."""
    keys=(
        'id','work_type','film_title','film_year','rights_evidence','license',
        'rights_pass','relevance_evidence','relevance_pass','anti_repeat_evidence',
        'dedup_60d_pass','live_readback_pass','ready_checked_at','schedule',
        'caption_chunks','scene_plan','music_track','source_url','source_sha256'
    )
    return _digest({k:item.get(k) for k in keys})


def item_fingerprint(item):
    return prepared_asset_fingerprint(item)
