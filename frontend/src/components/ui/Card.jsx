const Card = ({
  children,
  className = "",
  hover = false,
  padding = "md",
  ...props
}) => {
  const paddings = {
    sm: "p-4",
    md: "p-6",
    lg: "p-8",
  };

  return (
    <div
      className={`
        rounded-2xl
        border
        border-slate-200
        bg-white
        shadow-sm
        ${hover ? 'card-hover cursor-pointer' : ''}
        ${paddings[padding]}
        ${className}
      `}
      {...props}
    >
      {children}
    </div>
  );
};

const CardHeader = ({ children, className = "" }) => (
  <div className={`mb-4 ${className}`}>{children}</div>
);

const CardTitle = ({ children, className = "" }) => (
  <h3 className={`text-lg font-semibold text-slate-900 ${className}`}>{children}</h3>
);

const CardDescription = ({ children, className = "" }) => (
  <p className={`text-sm text-slate-500 mt-1 ${className}`}>{children}</p>
);

const CardContent = ({ children, className = "" }) => (
  <div className={className}>{children}</div>
);

const CardFooter = ({ children, className = "" }) => (
  <div className={`mt-4 pt-4 border-t border-slate-100 ${className}`}>{children}</div>
);

Card.Header = CardHeader;
Card.Title = CardTitle;
Card.Description = CardDescription;
Card.Content = CardContent;
Card.Footer = CardFooter;

export default Card;
