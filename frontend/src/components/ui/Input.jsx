const Input = ({
  label,
  error,
  helper,
  className = "",
  disabled = false,
  ...props
}) => {
  return (
    <div className="w-full">
      {label && (
        <label className="input-label">{label}</label>
      )}
      <input
        className={`
          input
          ${error ? 'input-error' : ''}
          ${disabled ? 'opacity-60 cursor-not-allowed' : ''}
          ${className}
        `}
        disabled={disabled}
        {...props}
      />
      {error && (
        <p className="input-error-message">{error}</p>
      )}
      {helper && !error && (
        <p className="input-helper">{helper}</p>
      )}
    </div>
  );
};

export default Input;
