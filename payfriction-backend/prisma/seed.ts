import 'dotenv/config';
import { PrismaClient } from '@prisma/client';
import { Pool } from 'pg';
import { PrismaPg } from '@prisma/adapter-pg';

// Initialize Prisma exactly like we did in NestJS
const pool = new Pool({ connectionString: process.env.DATABASE_URL });
const adapter = new PrismaPg(pool);
const prisma = new PrismaClient({ adapter });

async function main() {
  console.log('🌱 Starting database seed...');

  // 1. Create Payment Gateways
  const stripe = await prisma.paymentGateway.upsert({
    where: { name: 'Stripe' },
    update: {},
    create: { name: 'Stripe' },
  });
  
  const razorpay = await prisma.paymentGateway.upsert({
    where: { name: 'Razorpay' },
    update: {},
    create: { name: 'Razorpay' },
  });

  // 2. Create Bank Response Codes (From PRD)
  const codeSuccess = await prisma.bankResponseCode.upsert({
    where: { code: '00' },
    update: {},
    create: { code: '00', meaning: 'Approved', classification: 'Success', actionRequired: 'None' },
  });

  const codeInsuffFunds = await prisma.bankResponseCode.upsert({
    where: { code: '51' },
    update: {},
    create: { code: '51', meaning: 'Insufficient Funds', classification: 'Temporary Friction', actionRequired: 'Retry Later' },
  });

  const codeExpired = await prisma.bankResponseCode.upsert({
    where: { code: '54' },
    update: {},
    create: { code: '54', meaning: 'Expired Card', classification: 'Permanent Failure', actionRequired: 'Stop Retry' },
  });

  // 3. Create a Merchant & Customer
  const merchant = await prisma.merchant.create({
    data: { name: 'Global Tech SaaS', industry: 'Software' },
  });

  const customer = await prisma.customer.create({
    data: { email: 'finance@enterprise.com', customerSegment: 'Enterprise' },
  });

  // 4. Generate Transactions & Payment Attempts
  console.log('Generating transactions...');
  
  // Successful Transaction
  await prisma.transaction.create({
    data: {
      amount: 1500.00,
      status: 'SUCCESS',
      merchantId: merchant.id,
      customerId: customer.id,
      attempts: {
        create: [{ attemptNumber: 1, isSuccess: true, gatewayId: stripe.id, responseCodeId: codeSuccess.id }],
      },
    },
  });

  // Failed Transaction (Revenue at Risk) - Insufficient Funds
  await prisma.transaction.create({
    data: {
      amount: 450.00,
      status: 'FAILED',
      merchantId: merchant.id,
      customerId: customer.id,
      attempts: {
        create: [{ attemptNumber: 1, isSuccess: false, gatewayId: razorpay.id, responseCodeId: codeInsuffFunds.id }],
      },
    },
  });

  // Failed Transaction (Revenue Lost) - Expired Card
  await prisma.transaction.create({
    data: {
      amount: 80.00,
      status: 'FAILED',
      merchantId: merchant.id,
      customerId: customer.id,
      attempts: {
        create: [{ attemptNumber: 1, isSuccess: false, gatewayId: stripe.id, responseCodeId: codeExpired.id }],
      },
    },
  });

  console.log('✅ Database seeded successfully!');
}

main()
  .catch((e) => {
    console.error('❌ Seeding failed:', e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });