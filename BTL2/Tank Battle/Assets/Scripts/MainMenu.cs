using UnityEngine;
using UnityEngine.SceneManagement;

public class MainMenuController : MonoBehaviour
{
    public string mapSelectionSceneName = "MapSelectionScene";

    void Start()
    {
        // Play intro/menu background music
        if (AudioManager.Instance != null)
        {
            AudioManager.Instance.PlayIntroMusic();
        }
    }

    public void PlayGame()
    {
        // Play click sound
        if (AudioManager.Instance != null)
        {
            AudioManager.Instance.PlayClick();
        }
        
        Debug.Log("Loading Map Selection...");
        SceneManager.LoadScene(mapSelectionSceneName);
    }

    public void QuitGame()
    {
        // Play click sound
        if (AudioManager.Instance != null)
        {
            AudioManager.Instance.PlayClick();
        }
        
        Debug.Log("Quitting Game...");
        
        Application.Quit();
        
        #if UNITY_EDITOR
        UnityEditor.EditorApplication.isPlaying = false;
        #endif
    }
}