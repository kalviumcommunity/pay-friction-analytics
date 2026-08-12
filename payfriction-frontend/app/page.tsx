import SummaryCards from "@/components/SummaryCards"; // <-- This will also work perfectly

export default function Home() {
  return (
    <main className="max-w-6xl mx-auto p-8">
      <header className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">PayFriction Overview</h1>
        <p className="text-gray-500 mt-1">Real-time payment failure analytics</p>
      </header>

      <SummaryCards />
    </main>
  );
}