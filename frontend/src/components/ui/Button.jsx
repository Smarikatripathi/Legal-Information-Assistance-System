const Button = ({
  children,
  variant = "primary",
  size = "md",
  type = "button",
  className = "",
  ...props
}) => {
  const variants = {
    primary: "bg-blue-800 text-white hover:bg-blue-900",
    gradient:
      "bg-gradient-to-r from-red-700 via-red-600 to-blue-800 text-white hover:scale-[1.02] shadow-lg",
  };

  const sizes = {
    sm: "px-3 py-1 text-sm",
    md: "px-5 py-2 text-base",
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