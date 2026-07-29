const Button = ({
  children,
  variant = "primary",
  size = "md",
  type = "button",
  className = "",
  disabled = false,
  loading = false,
  ...props
}) => {

  const variants = {
    primary:
      "bg-[#084FF4] text-white hover:bg-[#063fd1] focus:ring-[#084FF4] focus:ring-offset-2",

    danger:
      "bg-[#C30A1C] text-white hover:bg-[#a70917] focus:ring-[#C30A1C] focus:ring-offset-2",

    secondary:
      "bg-slate-100 text-slate-700 hover:bg-slate-200 focus:ring-slate-400 focus:ring-offset-2",

    outline:
      "border border-slate-300 bg-white text-slate-700 hover:bg-slate-100 hover:border-slate-400 focus:ring-slate-400 focus:ring-offset-2",

    gradient:
      "bg-gradient-to-r from-red-700 to-blue-800 text-white hover:from-red-800 hover:to-blue-900 focus:ring-blue-500 focus:ring-offset-2",
  };


  const sizes = {
    sm: "px-3 py-1.5 text-sm",
    md: "px-5 py-2.5 text-base",
    lg: "px-6 py-3 text-lg",
  };


  return (
    <button
      type={type}
      disabled={disabled || loading}
      className={`
        inline-flex
        items-center
        justify-center
        gap-2
        rounded-xl
        font-medium
        transition-all
        duration-200
        cursor-pointer
        focus:outline-none
        focus:ring-2
        focus:ring-offset-2
        active:scale-95
        disabled:opacity-50
        disabled:cursor-not-allowed
        disabled:active:scale-100

        ${variants[variant]}
        ${sizes[size]}
        ${className}
      `}
      {...props}
    >
      {loading && (
        <svg
          className="animate-spin h-4 w-4"
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
        >
          <circle
            className="opacity-25"
            cx="12"
            cy="12"
            r="10"
            stroke="currentColor"
            strokeWidth="4"
          ></circle>
          <path
            className="opacity-75"
            fill="currentColor"
            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
          ></path>
        </svg>
      )}
      {children}
    </button>
  );
};


export default Button;