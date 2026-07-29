import { ChevronRight } from "lucide-react";

const Breadcrumb = ({ items }) => {
  return (
    <nav className="flex items-center gap-2 text-sm text-slate-500 mb-6">
      {items.map((item, index) => (
        <div key={index} className="flex items-center gap-2">
          {index > 0 && <ChevronRight size={16} />}
          {item.href ? (
            <a
              href={item.href}
              className="hover:text-[#084FF4] transition-colors"
            >
              {item.label}
            </a>
          ) : (
            <span className="font-medium text-slate-900">{item.label}</span>
          )}
        </div>
      ))}
    </nav>
  );
};

export default Breadcrumb;
