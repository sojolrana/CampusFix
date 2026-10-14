
import Link from "next/link";

/** Render the public CampusFix landing page. */
export default function HomePage() {
  return (
    <main className="flex min-h-screen items-center bg-slate-50 px-6 py-16">
      <div className="mx-auto w-full max-w-5xl">
        <nav className="flex items-center justify-between">
          <span className="text-xl font-bold text-blue-700">CampusFix</span>
          <div className="flex items-center gap-4">
            <Link href="/login" className="text-sm font-medium">
              Sign in
            </Link>
            <Link
              href="/register"
              className="rounded-lg bg-blue-700 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-800"
            >
              Get started
            </Link>
          </div>
        </nav>

        <section className="max-w-3xl py-24">
          <p className="font-semibold text-blue-700">
            A better campus, together.
          </p>
          <h1 className="mt-5 text-4xl font-bold tracking-tight text-slate-900 sm:text-6xl">
            Report campus issues. Track real progress.
          </h1>
          <p className="mt-6 max-w-2xl text-lg leading-8 text-slate-600">
            CampusFix connects students, campus staff, and administrators
            to make reporting problems and coordinating resolutions easier.
          </p>
          <div className="mt-8 flex flex-wrap gap-4">
            <Link
              href="/register"
              className="rounded-lg bg-blue-700 px-5 py-3 font-semibold text-white hover:bg-blue-800"
            >
              Create an account
            </Link>
            <Link
              href="/login"
              className="rounded-lg border border-slate-300 bg-white px-5 py-3 font-semibold hover:bg-slate-100"
            >
              Sign in
            </Link>
          </div>
        </section>

        <footer className="border-t border-slate-200 pt-6 text-sm text-slate-500">
          CampusFix · Campus issue reporting and resolution
        </footer>
      </div>
    </main>
  );
}
