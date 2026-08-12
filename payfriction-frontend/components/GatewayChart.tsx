"use client";

import { useQuery } from "@tanstack/react-query";
import axios from "axios";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

// Define the shape of the data from our NestJS API
interface GatewayData {
  gateway: string;
  totalAttempts: number;
  successful: number;
  failed: number;
  successRate: string;
}

export default function GatewayChart() {
  const { data, isLoading, isError } = useQuery<GatewayData[]>({
    queryKey: ["gateway-performance"],
    queryFn: async () => {
      const response = await axios.get("http://localhost:3001/analytics/gateways");
      return response.data;
    },
  });

  if (isLoading) return <div className="p-4 text-gray-500 bg-white rounded-xl border border-gray-200 h-96 flex items-center justify-center">Loading chart...</div>;
  if (isError) return <div className="p-4 text-red-500 bg-white rounded-xl border border-gray-200 h-96 flex items-center justify-center">Failed to load chart.</div>;

  return (
    <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm mb-8">
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-gray-900">Gateway Performance</h3>
        <p className="text-sm text-gray-500">Successful vs Failed transactions by provider</p>
      </div>
      
      {/* Recharts needs a set height to render properly inside a ResponsiveContainer */}
      <div className="h-80 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={data}
            margin={{ top: 20, right: 30, left: 0, bottom: 5 }}
          >
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E5E7EB" />
            <XAxis dataKey="gateway" axisLine={false} tickLine={false} />
            <YAxis axisLine={false} tickLine={false} />
            <Tooltip 
              cursor={{ fill: '#F3F4F6' }}
              contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
            />
            <Legend iconType="circle" />
            <Bar dataKey="successful" name="Successful" fill="#10B981" radius={[4, 4, 0, 0]} maxBarSize={60} />
            <Bar dataKey="failed" name="Failed" fill="#EF4444" radius={[4, 4, 0, 0]} maxBarSize={60} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}