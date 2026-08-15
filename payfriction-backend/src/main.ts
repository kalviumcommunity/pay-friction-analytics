import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);
  
  // Force the server to bind to IPv4
  await app.listen(3000, '127.0.0.1'); 
}
bootstrap();