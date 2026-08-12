import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);
  
  // Enable CORS so our Next.js frontend can talk to this API
  app.enableCors();
  
  await app.listen(process.env.PORT ?? 3001);
}
bootstrap();