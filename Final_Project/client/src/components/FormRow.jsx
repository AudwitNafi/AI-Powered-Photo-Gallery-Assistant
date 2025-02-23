function FormRow({ type, name, labelText, defaultValue, placeholder }) {
  return (
    <div className="form-row">
      <label htmlFor={name} className="form-label">
        {labelText || name}
      </label>
      <input
        type={type}
        id={name}
        name={name}
        className={type === "textarea" ? "text-area form-input" : "form-input"}
        defaultValue={defaultValue || ""}
        placeholder={placeholder ? placeholder : ""}
        required
      />
    </div>
  );
}

export default FormRow;
