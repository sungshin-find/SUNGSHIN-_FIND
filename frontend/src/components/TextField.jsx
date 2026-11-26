import { useId } from "react";

// 라벨 + 입력칸 + (안내 문구 | 에러 문구) 묶음
// suffix 를 주면 입력칸 오른쪽에 고정 글자가 붙음 (예: @sungshin.ac.kr)
export function TextField({ label, hint, error, suffix, ...inputProps }) {
  const id = useId();
  const messageId = `${id}-msg`;
  const message = error || hint;

  return (
    <div className={`field${error ? " field--error" : ""}`}>
      <label htmlFor={id} className="field__label">
        {label}
      </label>
      <div className="field__control">
        <input
          id={id}
          className="field__input"
          aria-invalid={error ? true : undefined}
          aria-describedby={message ? messageId : undefined}
          {...inputProps}
        />
        {suffix && <span className="field__suffix">{suffix}</span>}
      </div>
      {message && (
        <p id={messageId} className={error ? "field__error" : "field__hint"}>
          {message}
        </p>
      )}
    </div>
  );
}
