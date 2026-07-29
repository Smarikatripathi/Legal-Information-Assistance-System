import { useEffect, useState } from "react";
import { useParams, useNavigate, useOutletContext } from "react-router-dom";
import { MapPin, BriefcaseBusiness, Mail, User, ArrowLeft, Calendar, GraduationCap, Award } from "lucide-react";
import { FaFacebook } from "react-icons/fa";

import { getLawyers } from "../services/lawyerService";
import Breadcrumb from "../components/ui/Breadcrumb";

const LawyerProfile = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [lawyer, setLawyer] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchLawyer();
  }, [id]);

  const fetchLawyer = async () => {
    try {
      setLoading(true);
      const lawyers = await getLawyers();
      const foundLawyer = lawyers.find((l) => l.id === parseInt(id));
      setLawyer(foundLawyer);
    } catch (error) {
      console.error("Failed to load lawyer:", error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="text-slate-500">Loading lawyer profile...</div>
      </div>
    );
  }

  if (!lawyer) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="text-slate-500">Lawyer not found</div>
      </div>
    );
  }

  return (
    <div className="min-h-full overflow-y-auto p-6 md:p-8">
      {/* Breadcrumb */}
      <Breadcrumb
        items={[
          { label: "Dashboard", href: "/dashboard" },
          { label: "Lawyers Directory", href: "/dashboard/lawyers" },
          { label: lawyer.full_name },
        ]}
      />

      {/* Back Button */}
      <button
        onClick={() => navigate("/dashboard/lawyers")}
        className="mb-6 flex items-center gap-2 text-slate-600 hover:text-[#084FF4] transition-colors font-medium"
      >
        <ArrowLeft size={20} />
        Back to Lawyers Directory
      </button>

      {/* Professional Resume Layout */}
      <div className="max-w-5xl mx-auto space-y-6">
        {/* Header Section */}
        <div className="rounded-2xl border border-slate-200 bg-white p-8 shadow-lg">
          <div className="flex flex-col lg:flex-row items-start gap-8">
            {/* Profile Photo */}
            <div className="shrink-0">
              {lawyer.profile_image ? (
                <img
                  src={lawyer.profile_image}
                  alt={lawyer.full_name}
                  className="h-48 w-48 rounded-2xl object-cover shadow-md border-4 border-slate-100"
                />
              ) : (
                <div className="flex h-48 w-48 items-center justify-center rounded-2xl bg-gradient-to-br from-[#C30A1C] to-[#8a0614] text-6xl font-bold text-white shadow-md border-4 border-slate-100">
                  {lawyer.full_name.charAt(0)}
                </div>
              )}
            </div>

            {/* Name and Title */}
            <div className="flex-1 min-w-0">
              <div className="mb-4">
                <h1 className="text-4xl font-bold text-slate-900 tracking-tight">{lawyer.full_name}</h1>
                <p className="mt-2 text-2xl text-[#084FF4] font-semibold">{lawyer.specialization}</p>
              </div>

              {/* Quick Info */}
              <div className="flex flex-wrap gap-6 mb-6 text-sm">
                <div className="flex items-center gap-2 text-slate-600">
                  <MapPin size={18} className="text-[#C30A1C]" />
                  <span className="font-medium">{lawyer.city}</span>
                </div>
                <div className="flex items-center gap-2 text-slate-600">
                  <BriefcaseBusiness size={18} className="text-[#084FF4]" />
                  <span className="font-medium">{lawyer.years_of_experience} years experience</span>
                </div>
                <div className="flex items-center gap-2 text-slate-600">
                  <Mail size={18} className="text-slate-500" />
                  <span className="font-medium">{lawyer.email}</span>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex flex-wrap gap-3">
                {lawyer.email && (
                  <a
                    href={`https://mail.google.com/mail/?view=cm&fs=1&to=${lawyer.email}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-2 px-6 py-3 rounded-xl bg-[#084FF4] text-white text-sm font-semibold hover:bg-[#063fd1] transition-all duration-200 shadow-md hover:shadow-lg focus:outline-none focus:ring-2 focus:ring-[#084FF4] focus:ring-offset-2"
                  >
                    <Mail size={18} />
                    Send Email
                  </a>
                )}
                <a
                  href="https://www.facebook.com/martha.bastola"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-2 px-6 py-3 rounded-xl bg-[#1877F2] text-white text-sm font-semibold hover:bg-[#0d5bb5] transition-all duration-200 shadow-md hover:shadow-lg focus:outline-none focus:ring-2 focus:ring-[#1877F2] focus:ring-offset-2"
                >
                  <FaFacebook size={18} />
                  Facebook
                </a>
              </div>
            </div>
          </div>
        </div>

        {/* Two Column Layout */}
        <div className="grid gap-6 lg:grid-cols-3">
          {/* Left Column - Main Content */}
          <div className="lg:col-span-2 space-y-6">
            {/* Professional Summary */}
            {lawyer.bio && (
              <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
                <h2 className="text-xl font-bold text-slate-900 mb-4 flex items-center gap-2">
                  <User size={24} className="text-[#084FF4]" />
                  Professional Summary
                </h2>
                <p className="text-slate-600 leading-relaxed text-base">{lawyer.bio}</p>
              </div>
            )}

            {/* Experience */}
            <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
              <h2 className="text-xl font-bold text-slate-900 mb-4 flex items-center gap-2">
                <BriefcaseBusiness size={24} className="text-[#084FF4]" />
                Professional Experience
              </h2>
              <div className="space-y-4">
                <div className="border-l-4 border-[#084FF4] pl-4 py-2">
                  <h3 className="font-semibold text-slate-900 text-lg">{lawyer.specialization}</h3>
                  <p className="text-slate-600 mt-1 flex items-center gap-2">
                    <Calendar size={16} className="text-slate-400" />
                    <span>{lawyer.years_of_experience} years of professional experience</span>
                  </p>
                  <p className="text-slate-500 mt-2 text-sm leading-relaxed">
                    Specialized in {lawyer.specialization.toLowerCase()} with extensive experience in legal practice, case management, and client representation.
                  </p>
                </div>
              </div>
            </div>

            {/* Education */}
            <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
              <h2 className="text-xl font-bold text-slate-900 mb-4 flex items-center gap-2">
                <GraduationCap size={24} className="text-[#084FF4]" />
                Education
              </h2>
              <div className="space-y-4">
                <div className="border-l-4 border-[#C30A1C] pl-4 py-2">
                  <h3 className="font-semibold text-slate-900 text-lg">Bachelor of Laws (LL.B)</h3>
                  <p className="text-slate-600 mt-1">Tribhuvan University, Nepal</p>
                  <p className="text-slate-500 mt-1 text-sm">Graduated with honors</p>
                </div>
              </div>
            </div>
          </div>

          {/* Right Column - Sidebar */}
          <div className="space-y-6">
            {/* Skills & Expertise */}
            <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
              <h2 className="text-xl font-bold text-slate-900 mb-4 flex items-center gap-2">
                <Award size={24} className="text-[#084FF4]" />
                Skills & Expertise
              </h2>
              <div className="flex flex-wrap gap-2">
                {["Legal Consultation", "Case Management", "Client Relations", "Legal Research", "Court Proceedings", "Contract Law", "Civil Litigation"].map((skill) => (
                  <span
                    key={skill}
                    className="px-3 py-1.5 rounded-lg bg-slate-100 text-slate-700 text-sm font-medium hover:bg-slate-200 transition-colors"
                  >
                    {skill}
                  </span>
                ))}
              </div>
            </div>

            {/* Practice Areas */}
            <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
              <h2 className="text-xl font-bold text-slate-900 mb-4 flex items-center gap-2">
                <BriefcaseBusiness size={24} className="text-[#C30A1C]" />
                Practice Areas
              </h2>
              <ul className="space-y-2 text-sm text-slate-600">
                <li className="flex items-center gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-[#084FF4]" />
                  Civil Law
                </li>
                <li className="flex items-center gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-[#084FF4]" />
                  Criminal Law
                </li>
                <li className="flex items-center gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-[#084FF4]" />
                  Family Law
                </li>
                <li className="flex items-center gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-[#084FF4]" />
                  Property Law
                </li>
                <li className="flex items-center gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-[#084FF4]" />
                  Corporate Law
                </li>
              </ul>
            </div>

            {/* Languages */}
            <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
              <h2 className="text-xl font-bold text-slate-900 mb-4 flex items-center gap-2">
                <User size={24} className="text-[#084FF4]" />
                Languages
              </h2>
              <div className="space-y-2 text-sm text-slate-600">
                <div className="flex justify-between">
                  <span>Nepali</span>
                  <span className="text-slate-400">Native</span>
                </div>
                <div className="flex justify-between">
                  <span>English</span>
                  <span className="text-slate-400">Fluent</span>
                </div>
                <div className="flex justify-between">
                  <span>Hindi</span>
                  <span className="text-slate-400">Professional</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LawyerProfile;
