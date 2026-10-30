

export const handleQuestionSubmit = async (
    question: string,
    setLoading: (value: boolean) => void,
    setAnswer: (value: string) => void,
    onError: (message: string) => void,
) => {
    const trimmedQuestion = question.trim()

    setLoading(true)

    const params = new URLSearchParams({
      question: trimmedQuestion,
    });

    try {
        const response = await fetch(
          `/api/books/get_question?${params}`,
        );

        if (!response.ok) {
            throw new Error(`Ошибка сервера: ${response.status}`);
          }

          const result = await response.text();

        setAnswer(result)

    } catch (err: unknown) {
        const message = err instanceof Error ? err.message : 'Что-то пошло не так';
        onError(message);
    } finally {
      setLoading(false);
    }


}
