import type {ReactNode} from 'react';
import clsx from 'clsx';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';
import HomepageFeatures from '@site/src/components/HomepageFeatures';
import Heading from '@theme/Heading';

import styles from './index.module.css';

function HomepageHeader() {
  const {siteConfig} = useDocusaurusContext();
  return (
    <header className={styles.heroBanner}>
      <div className={styles.heroContainer}>
        <div className={styles.heroContent}>
          <div className={styles.heroTitle}>
            <span className={styles.titlePhysical}>Physical AI &</span>
            <span className={styles.titleHumanoid}>Humanoid Robotics</span>
          </div>

          <p className={styles.heroSubtitle}>
            Building Intelligent Humanoid Robots with AI – <span className={styles.specDriven}>Spec Driven Reusable Intelligence</span>
          </p>

          <div className={styles.badges}>
            <div className={styles.badge}>
              <span className={styles.badgeIcon}>✨</span>
              <span>Open Source</span>
            </div>
            <div className={styles.badge}>
              <span className={styles.badgeIcon}>🤝</span>
              <span>Co-Learning with AI</span>
            </div>
            <div className={styles.badge}>
              <span className={styles.badgeIcon}>🎯</span>
              <span>Spec-Driven Development</span>
            </div>
          </div>

          <div className={styles.buttons}>
            <Link
              className={clsx('button button--lg', styles.btnPrimary)}
              to="/docs/intro">
              <span>Start Learning</span>
              <span className={styles.btnIcon}>📚</span>
            </Link>
            <Link
              className={clsx('button button--lg', styles.btnSecondary)}
              to="https://github.com/ISMAIL-AHMED-SHAH/Hackathon-Book">
              <span>View on GitHub</span>
              <span className={styles.btnIcon}>⭐</span>
            </Link>
          </div>
        </div>
      </div>
    </header>
  );
}

export default function Home(): ReactNode {
  const {siteConfig} = useDocusaurusContext();
  return (
    <Layout
      title={`Hello from ${siteConfig.title}`}
      description="Description will go into a meta tag in <head />">
      <HomepageHeader />
      <main>
        <HomepageFeatures />

        {/* Author Section */}
        <div className={styles.authorSection}>
          <p className={styles.authorText}>
            ✨ Written & Designed by <span className={styles.authorName}>Ismail Ahmed Shah</span> ✨
          </p>
        </div>
      </main>
    </Layout>
  );
}
