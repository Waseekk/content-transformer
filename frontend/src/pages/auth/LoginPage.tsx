import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Link, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useAuth } from '../../contexts/AuthContext';
import { Button, Input, Card } from '../../components/common';
import { loginSchema, type LoginFormData } from '../../schemas/auth.schema';
import { useState } from 'react';
import toast from 'react-hot-toast';

export function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
  });

  const onSubmit = async (data: LoginFormData) => {
    setIsLoading(true);
    try {
      await login(data.email, data.password);
      toast.success('Login successful!');
      navigate('/dashboard');
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Login failed. Please check your credentials.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 via-indigo-50/50 to-purple-50 px-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-10">
          {/* Logo with Subtle Glow */}
          <motion.div
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ type: 'spring', stiffness: 200 }}
            className="flex justify-center mb-6"
          >
            <motion.img
              animate={{
                filter: [
                  'drop-shadow(0 0 10px rgba(99, 102, 241, 0.3))',
                  'drop-shadow(0 0 20px rgba(99, 102, 241, 0.5))',
                  'drop-shadow(0 0 10px rgba(99, 102, 241, 0.3))'
                ]
              }}
              transition={{ duration: 2, repeat: Infinity }}
              whileHover={{ scale: 1.05 }}
              src="/swiftor-logo.png"
              alt="Swiftor"
              className="h-20 w-20 rounded-2xl object-cover"
            />
          </motion.div>

          {/* Brand Name - Swift(bold) + oval o + r(small) */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.2 }}
            className="flex justify-center items-baseline mb-3"
          >
            {/* Swift - BOLD with gradient animation */}
            <motion.span
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.3, duration: 0.3 }}
              className="text-5xl font-extrabold tracking-tight logo-gradient-text"
            >
              Swift
            </motion.span>
            {/* Horizontal Oval O - with color animation */}
            <motion.span
              initial={{ opacity: 0, scaleX: 0 }}
              animate={{ opacity: 1, scaleX: 1 }}
              transition={{ delay: 0.4, type: 'spring', stiffness: 200 }}
              className="inline-flex items-center justify-center ml-0.5"
            >
              <span
                className="inline-block rounded-full logo-oval-border"
                style={{
                  width: '2.8rem',
                  height: '1.1rem',
                  marginBottom: '3px',
                  borderWidth: '3px',
                  borderStyle: 'solid'
                }}
              />
            </motion.span>
            {/* r - with gradient animation */}
            <motion.span
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.5 }}
              className="text-2xl font-normal logo-gradient-text"
              style={{ marginLeft: '1px' }}
            >
              r
            </motion.span>
          </motion.div>

          {/* Tagline */}
          <motion.p
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
            className="text-sm font-semibold tagline-shimmer"
          >
            AI powered clean and credible news
          </motion.p>
        </div>

        <Card>
          <h2 className="text-2xl font-bold text-gray-900 mb-6 text-center">Sign In</h2>

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <Input
              {...register('email')}
              type="email"
              label="Email Address"
              placeholder="you@example.com"
              error={errors.email?.message}
              autoComplete="email"
              required
            />

            <Input
              {...register('password')}
              type="password"
              label="Password"
              placeholder="••••••••"
              error={errors.password?.message}
              autoComplete="current-password"
              showPasswordToggle
              required
            />

            <Button
              type="submit"
              variant="primary"
              size="lg"
              fullWidth
              isLoading={isLoading}
            >
              Sign In
            </Button>
          </form>

          <div className="mt-6 text-center">
            <p className="text-sm text-gray-600">
              Don't have an account?{' '}
              <Link to="/register" className="text-blue-600 hover:text-blue-700 font-medium">
                Sign up
              </Link>
            </p>
          </div>
        </Card>

        <div className="mt-6 text-center">
          <p className="text-sm text-gray-400">A product of Data Insightopia</p>
        </div>

        <div className="mt-4 text-center text-sm text-gray-500">
          <p>Demo Credentials:</p>
          <p className="mt-1">Email: test@example.com</p>
          <p>Password: Test1234</p>
        </div>
      </div>
    </div>
  );
}
