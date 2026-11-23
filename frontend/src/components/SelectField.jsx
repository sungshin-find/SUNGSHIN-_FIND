import { useId } from "react";

// 라벨 + 드롭다운 (선택지는 서버의 /api/posts/choices/ 에서 받아온 [{ value, label }])
export function SelectField({ label, options, error, placeholder = "선택해 주세요", ...selectProps }) {
  const id = useId();
  return (
    <div className={`field${error ? " field--error" : ""}`}>
      <label htmlFor={id} className="field__label">
        {label}
      </label>
      <div className="field__control">
        <select id={id} className="field__input" aria-invalid={error ? true : undefined} {...selectProps}>
          <option value="" disabled>
            {placeholder}
          </option>
          {options.map((o) => (
            <option key={o.value} value={o.value}>
              {o.label}
            </option>
          ))}
        </select>
      </div>
      {error && <p className="field__error">{error}</p>}
    </div>
  );
}
