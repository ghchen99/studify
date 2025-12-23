function LoadingButtonContent({
  loading,
  loadingText,
  idleIcon,
  idleText,
}: {
  loading: boolean;
  loadingText: string;
  idleIcon: string;
  idleText: string;
}) {
  return loading ? (
    <>
      <span className="animate-spin">⏳</span>
      {loadingText}
    </>
  ) : (
    <>
      <span className="text-lg">{idleIcon}</span>
      {idleText}
    </>
  );
}

export { LoadingButtonContent };