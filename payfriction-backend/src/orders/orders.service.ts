import { Injectable } from '@nestjs/common';
import { PrismaService } from '../prisma/prisma.service';

@Injectable()
export class OrdersService {
  constructor(private prisma: PrismaService) {}

  // Fetch all transactions with their related data
  async getAllOrders() {
    return this.prisma.transaction.findMany({
      include: {
        customer: true,
        merchant: true,
        attempts: {
          include: {
            gateway: true,
            responseCode: true
          }
        }
      },
      orderBy: {
        createdAt: 'desc', 
      },
    });
  }

  // Calculate aggregated metrics for your dashboard
  async getDashboardMetrics() {
    const totalRevenue = await this.prisma.transaction.aggregate({
      _sum: {
        amount: true,
      },
      where: {
        status: 'SUCCESS', // Matching the status from your schema comments
      },
    });

    const totalCustomers = await this.prisma.customer.count();
    const totalTransactions = await this.prisma.transaction.count();
    const totalFailedAttempts = await this.prisma.paymentAttempt.count({
      where: { isSuccess: false }
    });

    return {
      revenue: totalRevenue._sum.amount || 0,
      totalCustomers,
      totalTransactions,
      failedAttempts: totalFailedAttempts,
    };
  }
}