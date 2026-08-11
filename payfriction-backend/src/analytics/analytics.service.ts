import { Injectable } from '@nestjs/common';
import { PrismaService } from '../prisma/prisma.service';

@Injectable()
export class AnalyticsService {
  constructor(private prisma: PrismaService) {}

  async getDashboardSummary() {
    // Aggregate the total amount of all FAILED transactions
    const revenueAtRisk = await this.prisma.transaction.aggregate({
      where: { status: 'FAILED' },
      _sum: { amount: true },
    });

    // Count how many transactions failed
    const failedCount = await this.prisma.transaction.count({
      where: { status: 'FAILED' },
    });

    return {
      revenueAtRisk: revenueAtRisk._sum.amount || 0,
      failedTransactions: failedCount,
    };
  }
}