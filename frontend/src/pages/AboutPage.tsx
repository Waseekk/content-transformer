/**
 * About Page — Swiftor by Data Insightopia
 */

import { motion } from 'framer-motion';
import { HiGlobe, HiSparkles, HiTranslate, HiNewspaper, HiLightningBolt, HiMail, HiPhone, HiLocationMarker, HiChip, HiChartBar, HiEye, HiHeart } from 'react-icons/hi';

const swiftorFeatures = [
  {
    icon: <HiTranslate className="w-5 h-5" />,
    title: 'AI-Powered Translation',
    desc: 'Translates English news into fluent Bangladeshi Bengali using advanced language models.',
  },
  {
    icon: <HiNewspaper className="w-5 h-5" />,
    title: 'Professional News Formats',
    desc: 'Generates Hard News & Soft News in the বাংলার কলম্বাস newspaper style.',
  },
  {
    icon: <HiSparkles className="w-5 h-5" />,
    title: 'Smart Enhancement',
    desc: 'Cleans raw web content and transforms it into publish-ready Bengali journalism.',
  },
  {
    icon: <HiLightningBolt className="w-5 h-5" />,
    title: 'Automated Scraping',
    desc: 'Scheduled scraping keeps your article library fresh with the latest travel and news content.',
  },
];

const services = [
  'Data Science Solutions',
  'AI / Machine Learning',
  'Agentic AI Solutions',
  'Business Intelligence',
  'Smart Dashboard Solutions',
  'Data Visualization',
  'Market Research',
  'Statistical Insights',
  'NLP Services',
];

const tools = ['Python', 'R', 'PySpark', 'TensorFlow', 'Power BI', 'Tableau', 'SPSS', 'SAS', 'Stata', 'GIS'];


export const AboutPage = () => {
  return (
    <div className="min-h-screen bg-gradient-to-b from-[#FAF8F5] to-[#F5F3F0]">
      <div className="w-full max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-12 space-y-8">

        {/* Swiftor Hero */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
          className="text-center"
        >
          <div className="inline-flex items-center gap-2 px-4 py-1.5 bg-indigo-50 border border-indigo-100 rounded-full text-indigo-600 text-sm font-medium mb-5">
            <HiSparkles className="w-4 h-4" />
            A Product by Data Insightopia
          </div>
          <h1 className="text-4xl font-bold text-gray-900 mb-3">About Swiftor</h1>
          <p className="text-gray-500 leading-relaxed max-w-xl mx-auto">
            Swiftor is an AI-driven content platform built for modern Bengali journalism — translating,
            formatting, and publishing news at speed, powered by the data science expertise of Data Insightopia.
          </p>
        </motion.div>

        {/* Swiftor Features */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 0.05 }}
          className="grid grid-cols-1 sm:grid-cols-2 gap-4"
        >
          {swiftorFeatures.map((f, i) => (
            <div key={i} className="bg-white rounded-2xl border border-gray-100 shadow-sm p-5 flex gap-4">
              <div className="flex-shrink-0 w-10 h-10 rounded-xl bg-indigo-50 text-indigo-600 flex items-center justify-center">
                {f.icon}
              </div>
              <div>
                <h3 className="font-semibold text-gray-900 mb-1 text-sm">{f.title}</h3>
                <p className="text-xs text-gray-500 leading-relaxed">{f.desc}</p>
              </div>
            </div>
          ))}
        </motion.div>

        {/* Divider */}
        <div className="flex items-center gap-4">
          <div className="flex-1 h-px bg-gray-200" />
          <span className="text-xs text-gray-400 font-medium uppercase tracking-widest">Built by</span>
          <div className="flex-1 h-px bg-gray-200" />
        </div>

        {/* Data Insightopia — Vision & Mission */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 0.1 }}
          className="bg-gradient-to-br from-indigo-600 to-violet-600 rounded-2xl p-8 text-white shadow-lg"
        >
          <div className="flex items-center gap-2 mb-2">
            <HiChip className="w-5 h-5 opacity-80" />
            <span className="text-lg font-bold">Data Insightopia</span>
          </div>
          <p className="text-white/70 text-sm mb-6">
            Bangladesh's AI & Data Science company — accelerating businesses with intelligent insights.
          </p>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="bg-white/10 rounded-xl p-4">
              <div className="flex items-center gap-2 mb-2">
                <HiEye className="w-4 h-4 opacity-80" />
                <span className="font-semibold text-sm">Our Vision</span>
              </div>
              <p className="text-white/80 text-xs leading-relaxed">
                To extract actionable insights through advanced data analytics, evolving businesses to succeed in a data-driven arena.
              </p>
            </div>
            <div className="bg-white/10 rounded-xl p-4">
              <div className="flex items-center gap-2 mb-2">
                <HiHeart className="w-4 h-4 opacity-80" />
                <span className="font-semibold text-sm">Our Mission</span>
              </div>
              <p className="text-white/80 text-xs leading-relaxed">
                Customer-centric intelligent decisions for optimum efficiency and sustainable growth — grounded in factual evidence and scientific precision.
              </p>
            </div>
          </div>
        </motion.div>

        {/* Services */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 0.15 }}
          className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6"
        >
          <div className="flex items-center gap-2 mb-4">
            <HiChartBar className="w-5 h-5 text-indigo-500" />
            <h2 className="font-semibold text-gray-900">Services</h2>
          </div>
          <div className="flex flex-wrap gap-2">
            {services.map((s) => (
              <span key={s} className="px-3 py-1.5 bg-indigo-50 text-indigo-700 text-xs font-medium rounded-lg border border-indigo-100">
                {s}
              </span>
            ))}
          </div>
        </motion.div>

        {/* Tools & Technologies */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 0.2 }}
          className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6"
        >
          <h2 className="font-semibold text-gray-900 text-sm mb-3">Tools & Technologies</h2>
          <div className="flex flex-wrap gap-2">
            {tools.map((t) => (
              <span key={t} className="px-2.5 py-1 bg-gray-50 text-gray-600 text-xs font-medium rounded-lg border border-gray-100">
                {t}
              </span>
            ))}
          </div>
        </motion.div>

        {/* Contact */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 0.25 }}
          className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6"
        >
          <h2 className="font-semibold text-gray-900 mb-4">Contact Data Insightopia</h2>
          <div className="space-y-3 text-sm text-gray-600">
            <div className="flex items-start gap-3">
              <HiLocationMarker className="w-4 h-4 text-indigo-400 mt-0.5 flex-shrink-0" />
              <span>Dhanmondi 10/a, Dhaka-1209</span>
            </div>
            <div className="flex items-center gap-3">
              <HiMail className="w-4 h-4 text-indigo-400 flex-shrink-0" />
              <a href="mailto:info@datainsightopia.com" className="text-indigo-600 hover:underline">
                info@datainsightopia.com
              </a>
            </div>
            <div className="flex items-center gap-3">
              <HiPhone className="w-4 h-4 text-indigo-400 flex-shrink-0" />
              <span>+880 1833-902231 &nbsp;|&nbsp; +880 1726-446657</span>
            </div>
          </div>
          <div className="mt-5">
            <a
              href="https://datainsightopia.com/"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 px-5 py-2.5 bg-indigo-600 text-white rounded-xl text-sm font-semibold hover:bg-indigo-700 transition-colors shadow-sm"
            >
              <HiGlobe className="w-4 h-4" />
              Visit datainsightopia.com
            </a>
          </div>
        </motion.div>

        <p className="text-center text-xs text-gray-300">
          Swiftor &copy; {new Date().getFullYear()} Data Insightopia. All rights reserved.
        </p>
      </div>
    </div>
  );
};
