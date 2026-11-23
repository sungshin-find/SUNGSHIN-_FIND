import { useEffect, useState } from "react";
import { useNavigate, useSearchParams } from "react-router";
import { errorMessage, fieldErrors } from "../api/errors";
import { createPost, getPostChoices } from "../api/posts";
import { SelectField } from "../components/SelectField";
import { TextField } from "../components/TextField";
import { todayInputValue } from "../utils/date";
import "../styles/posts.css";

const COPY = {
  LOST: { place: "잃어버린 곳", date: "잃어버린 날", detailHint: "예: 3층 열람실 창가 자리", descHint: "특징, 안에 든 물건, 연락 방법 등" },
  FOUND: { place: "주운 곳", date: "주운 날", detailHint: "예: 1층 정수기 옆", descHint: "지금 어디에 맡겨 두었는지 꼭 적어 주세요" },
};

export function PostFormPage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  const [choices, setChoices] = useState(null);
  const [form, setForm] = useState({
    post_type: searchParams.get("type") === "FOUND" ? "FOUND" : "LOST",
    title: "",
    category: "",
    color: "",
    location: "",
    location_detail: "",
    event_date: todayInputValue(),
    description: "",
  });
  const [errors, setErrors] = useState({});
  const [notice, setNotice] = useState("");
  const [submitting, setSubmitting] = useState(false);

  // 드롭다운 선택지는 백엔드 기준으로 받아옴 (선택지가 바뀌어도 프론트 수정 불필요)
  useEffect(() => {
    getPostChoices()
      .then(setChoices)
      .catch((err) => setNotice(errorMessage(err, "입력 항목을 불러오지 못했어요.")));
  }, []);

  const update = (key) => (e) => setForm((prev) => ({ ...prev, [key]: e.target.value }));
  const copy = COPY[form.post_type];

  async function handleSubmit(e) {
    e.preventDefault();
    setErrors({});
    setNotice("");
    setSubmitting(true);
    try {
      const created = await createPost(form);
      navigate(`/posts/${created.id}`, { replace: true });
    } catch (err) {
      const byField = fieldErrors(err);
      setErrors(byField);
      setNotice(Object.keys(byField).length ? "입력한 내용을 다시 확인해 주세요." : errorMessage(err));
      setSubmitting(false);
    }
  }

  const ready = form.title.trim() && form.category && form.color && form.location && form.event_date;

  return (
    <section className="post-form">
      <h1 className="page__title">게시물 등록</h1>
      <p className="page__lead">종류·색상·장소를 정확히 고를수록 비슷한 글을 잘 찾아줘요.</p>

      {notice && (
        <p className="notice notice--error" role="alert">
          {notice}
        </p>
      )}

      <form className="form" onSubmit={handleSubmit} noValidate>
        <fieldset className="type-switch">
          <legend className="field__label">어떤 글인가요?</legend>
          {[
            ["LOST", "물건을 잃어버렸어요"],
            ["FOUND", "물건을 주웠어요"],
          ].map(([value, text]) => (
            <label key={value} className={`type-switch__option type-switch__option--${value.toLowerCase()}`}>
              <input type="radio" name="post_type" value={value} checked={form.post_type === value} onChange={update("post_type")} />
              {text}
            </label>
          ))}
        </fieldset>

        <TextField
          label="제목"
          placeholder={form.post_type === "LOST" ? "예: 검정 반지갑 잃어버렸어요" : "예: 수정관에서 에어팟 케이스 주웠어요"}
          maxLength={100}
          value={form.title}
          onChange={update("title")}
          error={errors.title}
        />

        <div className="form__grid">
          <SelectField label="물건 종류" options={choices?.category ?? []} value={form.category} onChange={update("category")} error={errors.category} />
          <SelectField label="색상" options={choices?.color ?? []} value={form.color} onChange={update("color")} error={errors.color} />
          <SelectField label={copy.place} options={choices?.location ?? []} value={form.location} onChange={update("location")} error={errors.location} />
          <TextField
            label={copy.date}
            type="date"
            max={todayInputValue()}
            value={form.event_date}
            onChange={update("event_date")}
            error={errors.event_date}
          />
        </div>

        <TextField
          label="자세한 장소 (선택)"
          placeholder={copy.detailHint}
          maxLength={100}
          value={form.location_detail}
          onChange={update("location_detail")}
          error={errors.location_detail}
        />

        <div className="field">
          <label htmlFor="description" className="field__label">
            설명 (선택)
          </label>
          <div className="field__control">
            <textarea
              id="description"
              className="field__input"
              placeholder={copy.descHint}
              value={form.description}
              onChange={update("description")}
            />
          </div>
        </div>

        <div className="form__actions">
          <button type="button" className="btn btn--outline" onClick={() => navigate(-1)}>
            취소
          </button>
          <button className="btn btn--primary" disabled={submitting || !ready}>
            {submitting ? "등록하는 중…" : "등록하기"}
          </button>
        </div>
      </form>
    </section>
  );
}
