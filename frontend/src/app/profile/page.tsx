"use client";

import { FormEvent, useEffect, useState } from "react";
import { useRouter } from "next/navigation";

type UserProfile = {
  name: string;
  company: string;
  email: string;
  role: string;
};

type UserCV = {
  id: number;
  filename: string;
  created_at: string;
};

export default function ProfilePage() {
  const router = useRouter();
  const [userId, setUserId] = useState<string | null>(null);
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [cvs, setCvs] = useState<UserCV[]>([]);
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  
  const [name, setName] = useState("");
  const [company, setCompany] = useState("");
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const id = window.localStorage.getItem("sramp_user_id");
    if (!id) {
      router.push("/login");
      return;
    }
    setUserId(id);
    
    // Fetch Profile
    fetch(`http://localhost:5000/api/users/${id}/profile`)
      .then((res) => {
        if (!res.ok) {
          if (res.status === 404) {
            // User not found in DB (e.g. database was reset)
            window.localStorage.removeItem("sramp_user_id");
            window.localStorage.removeItem("sramp_user_role");
            window.localStorage.removeItem("sramp_user_name");
            window.dispatchEvent(new Event("auth-change"));
            router.push("/login");
            return null;
          }
          if (res.status !== 404) throw new Error("Failed to fetch profile");
        }
        return res.json();
      })
      .then((data) => {
        if (!data) return;
        setProfile(data);
        setName(data.name || "");
        setCompany(data.company || "");
      }).catch((err) => console.error(err));
      
    // Fetch CVs
    fetchCvs(id);
  }, [router]);

  const fetchCvs = async (id: string) => {
    try {
      const res = await fetch(`http://localhost:5000/api/users/${id}/cvs`);
      if (res.ok) setCvs(await res.json());
    } catch (err) {
      console.error("Failed to fetch CVs", err);
    }
  };

  const updateProfile = async (e: FormEvent) => {
    e.preventDefault();
    setMessage(null);
    try {
      const res = await fetch(`http://localhost:5000/api/users/${userId}/profile`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, company })
      });
      const data = await res.json();
      if (res.ok) {
        setMessage("Profile updated successfully!");
        window.localStorage.setItem("sramp_user_name", name);
        window.dispatchEvent(new Event("auth-change")); // Update Navbar
      } else {
        setError(data.error);
      }
    } catch {
      setError("Failed to update profile.");
    }
  };

  const handleUploadCV = async (e: FormEvent) => {
    e.preventDefault();
    if (!uploadFile || !userId) return;
    
    const formData = new FormData();
    formData.append("file", uploadFile);

    try {
      const res = await fetch(`http://localhost:5000/api/users/${userId}/cvs`, {
        method: "POST",
        body: formData,
      });
      if (res.ok) {
        setUploadFile(null);
        fetchCvs(userId);
      } else {
        const data = await res.json();
        setError(data.error || "Failed to upload CV");
      }
    } catch {
      setError("Server error during upload.");
    }
  };

  const deleteCV = async (cvId: number) => {
    if (!userId) return;
    try {
      await fetch(`http://localhost:5000/api/users/${userId}/cvs/${cvId}`, { method: "DELETE" });
      setCvs(cvs.filter((cv) => cv.id !== cvId));
    } catch (err) {
      console.error("Delete failed", err);
    }
  };

  if (!profile) return <div className="p-6">Loading profile...</div>;

  return (
    <div className="mx-auto max-w-2xl flex flex-col gap-8">
      <div className="rounded-xl border border-zinc-200 bg-white p-6 shadow-sm">
        <h1 className="text-2xl font-bold text-zinc-900">Your Profile</h1>
        <p className="mb-4 text-sm text-zinc-600">Update your personal details.</p>
        
        <form onSubmit={updateProfile} className="flex flex-col gap-4">
          <label className="flex flex-col gap-1 text-sm">
            <span className="font-medium text-zinc-700">Full Name</span>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="rounded-md border border-zinc-300 px-3 py-2 outline-none focus:border-zinc-500"
            />
          </label>
          
          {profile.role === "hr" && (
            <label className="flex flex-col gap-1 text-sm">
              <span className="font-medium text-zinc-700">Company</span>
              <input
                type="text"
                value={company}
                onChange={(e) => setCompany(e.target.value)}
                className="rounded-md border border-zinc-300 px-3 py-2 outline-none focus:border-zinc-500"
              />
            </label>
          )}

          {message && <div className="text-sm text-green-700 font-medium">{message}</div>}
          {error && <div className="text-sm text-red-700 font-medium">{error}</div>}

          <button type="submit" className="self-start rounded-md bg-zinc-900 px-4 py-2 text-sm font-semibold text-white hover:bg-zinc-800">
            Save Changes
          </button>
        </form>
      </div>

      {profile.role === "applicant" && (
        <div className="rounded-xl border border-zinc-200 bg-white p-6 shadow-sm">
          <h2 className="text-xl font-bold text-zinc-900 mb-2">My Saved Resumes</h2>
          <p className="mb-4 text-sm text-zinc-600">Upload your CVs here to quickly select them when applying for jobs.</p>
          
          <ul className="mb-6 flex flex-col gap-3">
            {cvs.length === 0 && <p className="text-sm text-zinc-500 italic">No CVs saved yet.</p>}
            {cvs.map(cv => (
              <li key={cv.id} className="flex items-center justify-between rounded-lg border px-4 py-3 bg-zinc-50">
                <a
                  href={`http://localhost:5000/api/users/${userId}/cvs/${cv.id}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm font-medium text-blue-600 hover:text-blue-800 hover:underline"
                  title="Click to view or download"
                >
                  {cv.filename}
                </a>
                <button onClick={() => deleteCV(cv.id)} className="text-sm text-red-600 hover:underline">Delete</button>
              </li>
            ))}
          </ul>

          <form onSubmit={handleUploadCV} className="flex items-center gap-3">
            <input 
              type="file" 
              accept=".pdf,.docx,.txt"
              onChange={(e) => setUploadFile(e.target.files ? e.target.files[0] : null)}
              className="text-sm file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-zinc-100 file:text-zinc-700 hover:file:bg-zinc-200 cursor-pointer"
            />
            <button type="submit" disabled={!uploadFile} className="rounded-md bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-500 disabled:opacity-50">
              Upload
            </button>
          </form>
        </div>
      )}
    </div>
  );
}
