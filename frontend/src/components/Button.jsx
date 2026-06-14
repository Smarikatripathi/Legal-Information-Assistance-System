const Button = ({
  children,
  variant = "primary",
  size = "md",
  type = "button",
  className = "",
  ...props
}) => {
  const variants = {
    primary:
      "bg-blue-800 text-white hover:bg-blue-900",

    secondary:
      "bg-slate-100 text-slate-800 hover:bg-slate-200",

    gradient:
      "bg-gradient-to-r from-red-700 via-red-600 to-blue-800 text-white hover:scale-[1.02] shadow-lg",

    outline:
      "border border-slate-300 text-slate-700 hover:bg-slate-50",

    danger:
      "bg-red-700 text-white hover:bg-red-800",

    ghost:
      "text-slate-600 hover:bg-slate-100",
  };

  const sizes = {
    sm: "px-3 py-2 text-sm",
    md: "px-5 py-3 text-base",
    lg: "px-6 py-3 text-lg",
  };

  return (
    <button
      type={type}
      className={`
        rounded-xl
        font-medium
        transition-all
        duration-200
        cursor-pointer

        ${variants[variant]}
        ${sizes[size]}
        ${className}
      `}
      {...props}
    >
      {children}
    </button>
  );
};

export default Button;