import JobDetailsPage from "@/components/jobs/JobDetailsPage";

export default async function Page({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const jobId = Number(id);
  return <JobDetailsPage jobId={jobId} />;
}

