// prisma.config.ts
import 'dotenv/config'; 
import { defineConfig, env } from 'prisma/config';

export default defineConfig({
  // Tell Prisma how to run your seed script
  migrations: {
    seed: 'npx ts-node prisma/seed.ts',
  },
  datasource: {
    url: env('DIRECT_URL'),
  },
});