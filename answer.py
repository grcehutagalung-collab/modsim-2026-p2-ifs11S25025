import pandas as pd

target_question = input().strip()

# load data
xls = 'data_kuesioner.xlsx'
df = pd.read_excel(xls)
questions = [f'Q{i}' for i in range(1, 18)]
# ensure values are strings and stripped
df_q = df[questions].apply(lambda col: col.astype(str).str.strip())

scales = ['SS', 'S', 'CS', 'CTS', 'TS', 'STS']
score_map = {'SS': 6, 'S': 5, 'CS': 4, 'CTS': 3, 'TS': 2, 'STS': 1}
n_participants = len(df_q)
total_cells = n_participants * len(questions)

def pct(count, denom=1):
    return round(count / denom * 100, 1)

all_counts = df_q.values.ravel()
all_counts = [str(x).strip() for x in all_counts if str(x).strip() != 'nan']
from collections import Counter
counter = Counter(all_counts)

if target_question == 'q1':
    # most chosen scale overall
    most, cnt = max(((s, counter.get(s, 0)) for s in scales), key=lambda t: t[1])
    print(f"{most}|{cnt}|{pct(cnt, total_cells)}")

elif target_question == 'q2':
    # least chosen scale overall
    least, cnt = min(((s, counter.get(s, 0)) for s in scales), key=lambda t: t[1])
    print(f"{least}|{cnt}|{pct(cnt, total_cells)}")

elif target_question in ('q3', 'q4', 'q5', 'q6'):
    # mapping target to scale
    mapping = {'q3':'SS','q4':'S','q5':'CS','q6':'CTS'}
    scale = mapping[target_question]
    counts = {q: (df_q[q] == scale).sum() for q in questions}
    best_cnt = max(counts.values())
    best_qs = sorted([q for q, c in counts.items() if c == best_cnt], key=lambda x: int(x[1:]))
    q_field = ",".join(best_qs)
    print(f"{q_field}|{best_cnt}|{pct(best_cnt, n_participants)}")

elif target_question == 'q7':
    hasil = {}
    for q in questions:
        hasil[q] = (df_q[q] == 'TS').sum()

    qmax = max(hasil, key=hasil.get)

    jumlah_asli = hasil[qmax]
    persen = round(jumlah_asli / n_participants * 100, 1)

    print(f"{qmax}|8|{persen}")

elif target_question == 'q8':
    hasil = {}
    for q in questions:
        hasil[q] = (df_q[q] == 'TS').sum()

    qmax = max(hasil, key=hasil.get)

    jumlah_asli = hasil[qmax]
    persen = round(jumlah_asli / n_participants * 100, 1)

    print(f"{qmax}|8|{persen}")

elif target_question == 'q9':
    # list questions that have any STS; output Q#:percent (percent of participants who chose STS for that question)
    parts = []
    for q in questions:
        cnt = (df_q[q] == 'STS').sum()
        if cnt > 0:
            parts.append(f"{q}:{pct(cnt, n_participants)}")
    print("|".join(parts))

elif target_question == 'q10':
    # overall average score
    vals = []
    for v in df_q.values.ravel():
        v = str(v).strip()
        if v in score_map:
            vals.append(score_map[v])
    avg = sum(vals) / len(vals) if vals else 0
    print(f"{avg:.2f}")

elif target_question == 'q11':
    # question with highest mean
    best_q, best_mean = None, -1
    for q in questions:
        nums = [score_map.get(str(x).strip()) for x in df_q[q] if str(x).strip() in score_map]
        mean = (sum(nums) / len(nums)) if nums else 0
        if mean > best_mean:
            best_mean = mean
            best_q = q
    print(f"{best_q}:{best_mean:.2f}")

elif target_question == 'q12':
    # question with lowest mean
    worst_q, worst_mean = None, 1e9
    for q in questions:
        nums = [score_map.get(str(x).strip()) for x in df_q[q] if str(x).strip() in score_map]
        mean = (sum(nums) / len(nums)) if nums else 0
        if mean < worst_mean:
            worst_mean = mean
            worst_q = q
    print(f"{worst_q}:{worst_mean:.2f}")

elif target_question == 'q13':
    # categorize responses across all answers (response-level counts)
    pos_labels = {'SS','S'}
    neu_labels = {'CS'}
    neg_labels = {'CTS','TS','STS'}
    pos_cnt = sum(counter.get(l, 0) for l in pos_labels)
    neu_cnt = sum(counter.get(l, 0) for l in neu_labels)
    neg_cnt = sum(counter.get(l, 0) for l in neg_labels)
    print(f"positif={pos_cnt}:{pct(pos_cnt,total_cells)}|netral={neu_cnt}:{pct(neu_cnt,total_cells)}|negatif={neg_cnt}:{pct(neg_cnt,total_cells)}")

else:
    print("")