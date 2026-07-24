# Model-Routing Cost Calculator

A small command-line tool that recommends which model tier to use per task
(by complexity), estimates the cost, and compares it against a naive
"everything on the top-tier model" baseline.

No dependencies. No network calls. Pure Python 3 standard library.

## Run it (one command)

```bash
python3 route.py examples/tasks.json
```

That's it — it prints a per-task routing table plus totals and % saved vs.
the naive baseline, and runs a built-in self-check first.

## How routing works

Each task gets a `complexity`:

| Complexity          | Route                                                  |
|----------------------|--------------------------------------------------------|
| `everyday`           | mid-tier model handles it directly                     |
| `judgment-heavy`      | one top-tier call plans it, mid-tier model executes     |
| `long-unattended`     | top-tier model orchestrates, mid-tier subagents execute |

The `judgment-heavy` and `long-unattended` routes are computed as a fraction
of the cost it would take to run the *entire* task on the top-tier model
(63% and 46% respectively), reflecting that a single planning/orchestration
call plus mid-tier execution lands close to top-tier quality for a fraction
of the spend.

## Input format

A JSON file with a pricing table and a list of tasks. See
`examples/tasks.json`:

```json
{
  "pricing": {
    "mid_tier": { "in": 3.00, "out": 15.00 },
    "top_tier": { "in": 15.00, "out": 75.00 }
  },
  "tasks": [
    { "name": "...", "complexity": "everyday", "input_tokens": 40000, "output_tokens": 8000 }
  ]
}
```

**The `pricing` table is example rates — edit me.** These are placeholders
in dollars per 1,000,000 tokens (input/output), not real prices for any
provider. The tool computes purely on whatever numbers you put in — check
your provider's current pricing page and edit the rates before trusting a
total.

## Self-check

`route.py` runs an assert-based self-check of the routing and cost math
every time it's invoked, before touching your input file. If the math is
ever wrong, it fails loudly instead of quoting a bad number.

## Other layers

- `skill/SKILL.md` — the same logic wrapped as a Claude skill.
- `paste-into-claude.md` — a single self-contained file you can paste
  straight into a chat with an LLM to get the same routing recommendation,
  no code required.

## License

MIT — see `LICENSE`.

---

# حاسبة تكلفة توجيه النماذج

أداة سطر أوامر صغيرة توصي بأي مستوى نموذج تستخدمه لكل مهمة (حسب درجة
تعقيدها)، وتُقدّر التكلفة، وتقارنها بخط أساس ساذج يفترض تشغيل كل شيء على
النموذج الأعلى فئة.

بدون أي تبعيات خارجية. بدون اتصال بالإنترنت. بايثون 3 (المكتبة القياسية
فقط).

## التشغيل (أمر واحد)

```bash
python3 route.py examples/tasks.json
```

هذا كل شيء — يطبع جدول التوجيه لكل مهمة مع الإجماليين ونسبة التوفير مقارنة
بخط الأساس الساذج، ويشغّل فحصًا ذاتيًا مدمجًا أولًا.

## آلية التوجيه

كل مهمة تحمل درجة تعقيد `complexity`:

| درجة التعقيد          | المسار                                                        |
|------------------------|----------------------------------------------------------------|
| `everyday` (يومية)     | نموذج متوسط الفئة ينفذها مباشرة                                |
| `judgment-heavy` (تتطلب حكمًا) | استدعاء واحد للنموذج الأعلى يضع الخطة، والنموذج المتوسط ينفذ  |
| `long-unattended` (طويلة بلا إشراف) | النموذج الأعلى ينسّق، ونماذج فرعية متوسطة الفئة تنفذ الخطوات |

مساري `judgment-heavy` و`long-unattended` يُحسَبان كنسبة من تكلفة تشغيل
المهمة **بالكامل** على النموذج الأعلى فئة (63% و46% على التوالي)، لأن
استدعاء تخطيط/تنسيق واحد مع تنفيذ متوسط الفئة يقترب من جودة النموذج الأعلى
بجزء بسيط من التكلفة.

## صيغة الإدخال

ملف JSON يحتوي جدول أسعار وقائمة مهام. راجع `examples/tasks.json`. **جدول
الأسعار أسعار توضيحية — عدّلها.** هذه أرقام افتراضية بالدولار لكل مليون
رمز (إدخال/إخراج)، وليست أسعارًا حقيقية لأي مزود. الأداة تحسب فقط بناءً على
الأرقام التي تُدخلها أنت — تحقق من صفحة تسعير مزودك الحالية وعدّل الأسعار
قبل الوثوق بأي إجمالي.

## الفحص الذاتي

يشغّل `route.py` فحصًا ذاتيًا (assert-based) لمنطق التوجيه وحساب التكلفة في
كل مرة يُستدعى فيها، قبل قراءة ملف الإدخال. إذا كان الحساب خاطئًا، يفشل
بوضوح بدلاً من طباعة رقم غير صحيح.

## الطبقات الأخرى

- `skill/SKILL.md` — نفس المنطق ضمن مهارة (skill) لـ Claude.
- `paste-into-claude.md` — ملف واحد قائم بذاته يمكنك لصقه مباشرة في محادثة
  مع نموذج لغوي للحصول على نفس توصية التوجيه، دون كتابة أي كود.

## الترخيص

MIT — راجع `LICENSE`.

---

More free tools + guides: [humoudalmunawer.vercel.app](https://humoudalmunawer.vercel.app/en/#tools)
